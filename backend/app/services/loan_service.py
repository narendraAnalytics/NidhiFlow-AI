import logging
import uuid

from sqlalchemy.orm import Session

from app.agents import LoanWorkflowState, loan_workflow_graph
from app.models.enums import LoanStatus
from app.models.loan_application import LoanApplication
from app.models.loan_status_history import LoanStatusHistory
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
    initial_state: LoanWorkflowState = {
        "loan_application_id": loan.id,
        "customer_id": loan.customer_id,
        "loan_status": loan.status.value,
        "documents": [
            {
                "id": str(doc.id),
                "document_type": doc.document_type.value,
                "firebase_url": doc.firebase_url,
                "status": doc.status.value,
            }
            for doc in documents
        ],
        "current_stage": None,
        "human_review_required": False,
        "agent_outputs": {},
        "errors": [],
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
            "errors": [*initial_state["errors"], "workflow invocation failed"],
        }


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
        "loan workflow completed: loan_application_id=%s stage=%s human_review_required=%s errors=%s",
        loan.id,
        workflow_result.get("current_stage"),
        workflow_result.get("human_review_required"),
        workflow_result.get("errors"),
    )
    return loan
