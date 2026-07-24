import logging
from datetime import datetime, timezone

from app.agents.document_intelligence.agent import run as run_document_intelligence
from app.agents.intake_supervisor.agent import run as run_intake_supervisor
from app.agents.pipeline_orchestrator.agent import run as run_pipeline_orchestrator
from app.agents.state import LoanWorkflowState
from app.agents.validation_compliance.agent import run as run_validation_compliance

logger = logging.getLogger(__name__)


def intake_supervisor_node(state: LoanWorkflowState) -> dict:
    """Deterministic intake triage: checks document-checklist completeness
    and loan-type-specific form-field completeness (both already available
    on state, before any OCR/LLM cost is spent downstream). No DB access,
    no LLM — reads only from state.
    """
    logger.info(
        "intake_supervisor: loan_application_id=%s documents=%d",
        state["loan_application_id"],
        len(state["documents"]),
    )
    try:
        summary = run_intake_supervisor(
            state["documents"],
            state.get("customer_profile", {}),
            state.get("loan_details", {}),
        )

        errors = list(state.get("errors", []))
        if summary.missing_documents:
            errors.append(f"Missing required documents: {', '.join(summary.missing_documents)}")
        if summary.missing_form_fields:
            errors.append(f"Missing required form fields: {', '.join(summary.missing_form_fields)}")
        errors.extend(summary.warnings)

        human_review_required = state.get("human_review_required", False) or summary.status == "failed"

        return {
            "current_stage": "intake_supervisor",
            "human_review_required": human_review_required,
            "errors": errors,
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "intake_supervisor": {
                    "document_count": len(state["documents"]),
                    "status": summary.status,
                    "summary": summary.model_dump(mode="json"),
                },
            },
        }
    except Exception:
        logger.exception(
            "intake_supervisor_node failed for loan_application_id=%s",
            state.get("loan_application_id"),
        )
        return {
            "current_stage": "intake_supervisor",
            "errors": [*state.get("errors", []), "intake_supervisor: unexpected error"],
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "intake_supervisor": {"status": "failed"},
            },
        }


def document_intelligence_node(state: LoanWorkflowState) -> dict:
    """Runs each document through Sarvam Vision OCR (job-based pipeline) and
    records the parsed markdown/JSON per document. No LLM classification or
    extraction here — document_type is the value already assigned at upload,
    and field-level extraction is deferred to a later reasoning agent.
    """
    logger.info(
        "document_intelligence: loan_application_id=%s documents=%d",
        state["loan_application_id"],
        len(state["documents"]),
    )
    try:
        results = run_document_intelligence(state["documents"])

        succeeded = sum(1 for r in results if r.status == "parsed")
        skipped = sum(1 for r in results if r.status == "skipped")
        if not results:
            overall_status = "parsed"
        elif skipped == len(results):
            overall_status = "skipped"
        elif succeeded + skipped == len(results):
            overall_status = "parsed"
        elif succeeded == 0:
            overall_status = "failed"
        else:
            overall_status = "partial"

        errors = list(state.get("errors", []))
        for result in results:
            if result.quality_warning:
                errors.append(
                    f"{result.document_type or result.document_id}: {result.quality_warning}"
                )

        return {
            "current_stage": "document_intelligence",
            "errors": errors,
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "document_intelligence": {
                    "status": overall_status,
                    "results": [r.model_dump(mode="json") for r in results],
                },
            },
        }
    except Exception:
        logger.exception(
            "document_intelligence_node failed for loan_application_id=%s",
            state.get("loan_application_id"),
        )
        return {
            "current_stage": "document_intelligence",
            "errors": [*state.get("errors", []), "document_intelligence: unexpected error"],
        }


def validation_compliance_node(state: LoanWorkflowState) -> dict:
    """Extracts structured borrower fields from OCR output via Gemma 4 /
    Gemini, then runs deterministic (no-LLM) cross-checks: PAN vs Aadhaar
    consistency, extracted IDs vs the customer record on file, required
    document presence, and an EMI-affordability check.
    """
    logger.info(
        "validation_compliance: loan_application_id=%s documents=%d",
        state["loan_application_id"],
        len(state["documents"]),
    )
    try:
        ocr_results = state.get("agent_outputs", {}).get("document_intelligence", {}).get("results", [])
        results, summary = run_validation_compliance(
            state["documents"],
            ocr_results,
            state.get("customer_profile", {}),
            state.get("loan_details", {}),
        )

        human_review_required = state.get("human_review_required", False) or summary.validation_status != "passed"

        return {
            "current_stage": "validation_compliance",
            "human_review_required": human_review_required,
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "validation_compliance": {
                    "documents": [r.model_dump(mode="json") for r in results],
                    "summary": summary.model_dump(mode="json"),
                },
            },
        }
    except Exception:
        logger.exception(
            "validation_compliance_node failed for loan_application_id=%s",
            state.get("loan_application_id"),
        )
        return {
            "current_stage": "validation_compliance",
            "human_review_required": True,
            "errors": [*state.get("errors", []), "validation_compliance: unexpected error"],
        }


def pipeline_orchestrator_node(state: LoanWorkflowState) -> dict:
    """Deterministic workflow controller: reads the OCR/validation outputs
    already in state and applies the Decision Matrix (missing docs / low
    confidence / validation failure -> human review, all-clear -> continue).
    No LLM calls, no DB access — only decides and records the decision.
    """
    logger.info(
        "pipeline_orchestrator: loan_application_id=%s",
        state["loan_application_id"],
    )
    finished_at = datetime.now(timezone.utc).isoformat()
    try:
        decision = run_pipeline_orchestrator(state)

        return {
            "current_stage": "pipeline_orchestrator",
            "next_stage": "END",
            "workflow_status": decision.workflow_status,
            "decision": decision.decision,
            "decision_reason": decision.decision_reason,
            "human_review_required": state.get("human_review_required", False) or decision.decision != "continue",
            "pipeline_completed": True,
            "pipeline_finished_at": finished_at,
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "pipeline_orchestrator": decision.model_dump(mode="json"),
            },
        }
    except Exception:
        logger.exception(
            "pipeline_orchestrator_node failed for loan_application_id=%s",
            state.get("loan_application_id"),
        )
        return {
            "current_stage": "pipeline_orchestrator",
            "next_stage": "END",
            "workflow_status": "Human Review",
            "decision": "human_review",
            "decision_reason": "pipeline_orchestrator: unexpected error",
            "human_review_required": True,
            "pipeline_completed": True,
            "pipeline_finished_at": finished_at,
            "errors": [*state.get("errors", []), "pipeline_orchestrator: unexpected error"],
        }
