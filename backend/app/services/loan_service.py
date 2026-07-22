import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.agents import LoanWorkflowState, loan_workflow_graph
from app.models.customer import Customer
from app.models.document_ocr_result import DocumentOcrResult
from app.models.document_validation_result import DocumentValidationResult
from app.models.enums import LoanStatus
from app.models.loan_application import LoanApplication
from app.models.loan_status_history import LoanStatusHistory
from app.models.loan_validation_summary import LoanValidationSummary
from app.models.workflow_event import WorkflowEvent
from app.models.workflow_execution import WorkflowExecution
from app.schemas.loan_application import LoanApplicationCreate, LoanApplicationSubmit
from app.services.document_service import list_documents_for_loan

logger = logging.getLogger(__name__)


class InvalidLoanStatusTransitionError(Exception):
    pass


def create_loan_application(db: Session, data: LoanApplicationCreate) -> LoanApplication:
    loan_application = LoanApplication(**data.model_dump(), status=LoanStatus.DRAFT)
    db.add(loan_application)
    db.commit()
    db.refresh(loan_application)
    return loan_application


def get_loan_application(db: Session, loan_id: uuid.UUID) -> LoanApplication | None:
    return db.query(LoanApplication).filter(LoanApplication.id == loan_id).first()


def run_loan_workflow(db: Session, loan: LoanApplication) -> LoanWorkflowState:
    documents = list_documents_for_loan(db, loan.id)
    customer = db.query(Customer).filter(Customer.id == loan.customer_id).first()

    initial_state: LoanWorkflowState = {
        "loan_application_id": loan.id,
        "customer_id": loan.customer_id,
        "loan_status": loan.status.value,
        "documents": [
            {
                "id": str(doc.id),
                "document_name": doc.document_name,
                "document_type": doc.document_type.value,
                "firebase_url": doc.firebase_url,
                "status": doc.status.value,
            }
            for doc in documents
        ],
        "customer_profile": {
            "pan": customer.pan,
            "aadhaar": customer.aadhaar,
            "full_name": customer.full_name,
        }
        if customer
        else {},
        "loan_details": {
            "requested_amount": float(loan.requested_amount) if loan.requested_amount is not None else None,
            "interest_rate": float(loan.interest_rate) if loan.interest_rate is not None else None,
            "tenure": loan.tenure,
            "monthly_income": float(loan.monthly_income) if loan.monthly_income is not None else None,
        },
        "current_stage": None,
        "human_review_required": False,
        "agent_outputs": {},
        "errors": [],
        "next_stage": None,
        "workflow_status": "Draft",
        "retry_count": 0,
        "decision": None,
        "decision_reason": None,
        "pipeline_completed": False,
        "pipeline_started_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_finished_at": None,
    }
    try:
        return loan_workflow_graph.invoke(initial_state)
    except Exception:
        logger.exception(
            "loan_workflow_graph.invoke failed for loan_application_id=%s", loan.id
        )
        return {
            **initial_state,
            "current_stage": "workflow_error",
            "workflow_status": "Human Review",
            "decision": "human_review",
            "human_review_required": True,
            "errors": [*initial_state["errors"], "workflow invocation failed"],
        }


def persist_document_ocr_results(db: Session, workflow_result: LoanWorkflowState) -> None:
    results = workflow_result.get("agent_outputs", {}).get("document_intelligence", {}).get("results", [])
    if not results:
        return

    for result in results:
        db.add(
            DocumentOcrResult(
                document_id=result["document_id"],
                document_type=result.get("document_type"),
                ocr_markdown=result.get("ocr_markdown"),
                ocr_json=result.get("ocr_json"),
                processing_status=result["status"],
                error_message=result.get("error"),
            )
        )
    db.commit()


def persist_validation_results(db: Session, loan: LoanApplication, workflow_result: LoanWorkflowState) -> None:
    validation = workflow_result.get("agent_outputs", {}).get("validation_compliance", {})
    documents = validation.get("documents", [])
    summary = validation.get("summary")

    for result in documents:
        db.add(
            DocumentValidationResult(
                document_id=result["document_id"],
                document_type=result.get("document_type"),
                extracted_fields=result.get("extracted_fields"),
                processing_status=result["status"],
                error_message=result.get("error"),
            )
        )

    if summary:
        db.add(
            LoanValidationSummary(
                loan_application_id=loan.id,
                validation_status=summary["validation_status"],
                confidence=summary["confidence"],
                missing_documents=summary["missing_documents"],
                field_mismatches=summary["field_mismatches"],
                warnings=summary["warnings"],
            )
        )

    if documents or summary:
        db.commit()


def persist_workflow_execution(
    db: Session, loan: LoanApplication, workflow_result: LoanWorkflowState
) -> WorkflowExecution:
    orchestrator_output = workflow_result.get("agent_outputs", {}).get("pipeline_orchestrator", {})
    started_at = workflow_result.get("pipeline_started_at")
    finished_at = workflow_result.get("pipeline_finished_at")
    duration = None
    if started_at and finished_at:
        try:
            duration = (
                datetime.fromisoformat(finished_at) - datetime.fromisoformat(started_at)
            ).total_seconds()
        except ValueError:
            duration = None

    execution = WorkflowExecution(
        loan_application_id=loan.id,
        workflow_status=workflow_result.get("workflow_status", "Human Review"),
        current_stage=workflow_result.get("current_stage"),
        completed_at=datetime.now(timezone.utc) if workflow_result.get("pipeline_completed") else None,
        duration=duration,
        retry_count=workflow_result.get("retry_count", 0),
    )
    db.add(execution)
    db.flush()

    for event in orchestrator_output.get("audit_trail", []):
        db.add(
            WorkflowEvent(
                workflow_execution_id=execution.id,
                stage=event["stage"],
                event_type=event["event_type"],
                message=event.get("message"),
            )
        )

    db.commit()
    db.refresh(execution)
    return execution


def submit_loan_application(
    db: Session, loan: LoanApplication, data: LoanApplicationSubmit
) -> LoanApplication:
    if loan.status != LoanStatus.DRAFT:
        raise InvalidLoanStatusTransitionError(
            f"Loan application is already {loan.status.value}, cannot submit again"
        )

    history = LoanStatusHistory(
        loan_application_id=loan.id,
        previous_status=loan.status,
        new_status=LoanStatus.DOCUMENTS_UPLOADED,
        changed_by=data.changed_by,
        notes=data.notes,
    )
    loan.status = LoanStatus.DOCUMENTS_UPLOADED
    db.add(history)
    db.commit()
    db.refresh(loan)

    workflow_result = run_loan_workflow(db, loan)
    logger.info(
        "loan workflow completed: loan_application_id=%s stage=%s decision=%s human_review_required=%s errors=%s",
        loan.id,
        workflow_result.get("current_stage"),
        workflow_result.get("decision"),
        workflow_result.get("human_review_required"),
        workflow_result.get("errors"),
    )
    persist_document_ocr_results(db, workflow_result)
    persist_validation_results(db, loan, workflow_result)
    persist_workflow_execution(db, loan, workflow_result)

    next_status = (
        LoanStatus.PROCESSING if workflow_result.get("decision") == "continue" else LoanStatus.HUMAN_REVIEW
    )
    pipeline_history = LoanStatusHistory(
        loan_application_id=loan.id,
        previous_status=loan.status,
        new_status=next_status,
        changed_by="pipeline_orchestrator",
        notes=workflow_result.get("decision_reason"),
    )
    loan.status = next_status
    db.add(pipeline_history)
    db.commit()
    db.refresh(loan)

    return loan
