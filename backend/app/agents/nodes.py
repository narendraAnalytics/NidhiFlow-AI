import logging

from app.agents.document_intelligence.agent import run as run_document_intelligence
from app.agents.state import LoanWorkflowState

logger = logging.getLogger(__name__)


def intake_supervisor_node(state: LoanWorkflowState) -> dict:
    """Deterministic bookkeeping node: flags applications with no documents
    for human review. No DB access, no LLM — reads only from state.
    """
    logger.info(
        "intake_supervisor: loan_application_id=%s documents=%d",
        state["loan_application_id"],
        len(state["documents"]),
    )
    try:
        errors = list(state.get("errors", []))
        human_review_required = state.get("human_review_required", False)
        if not state["documents"]:
            human_review_required = True
            errors.append("No documents attached at submission")

        return {
            "current_stage": "intake_supervisor",
            "human_review_required": human_review_required,
            "errors": errors,
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "intake_supervisor": {
                    "document_count": len(state["documents"]),
                    "status": "completed",
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

        return {
            "current_stage": "document_intelligence",
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
