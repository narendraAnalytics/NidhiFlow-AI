import logging

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
    """Placeholder node — no OCR, no LLM. Records a pending-analysis entry
    per document so later steps have a shape to extend into.
    """
    logger.info(
        "document_intelligence: loan_application_id=%s (placeholder, no-op)",
        state["loan_application_id"],
    )
    try:
        results = [
            {"document_type": doc.get("document_type"), "status": "pending_analysis"}
            for doc in state["documents"]
        ]
        return {
            "current_stage": "document_intelligence",
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "document_intelligence": {"status": "placeholder", "results": results},
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
