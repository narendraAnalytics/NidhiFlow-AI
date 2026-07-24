from app.agents.pipeline_orchestrator.decision_engine import build_audit_trail, evaluate
from app.agents.pipeline_orchestrator.schemas import OrchestrationDecision
from app.agents.state import LoanWorkflowState


def run(state: LoanWorkflowState) -> OrchestrationDecision:
    agent_outputs = state.get("agent_outputs", {})
    intake_summary = agent_outputs.get("intake_supervisor", {}).get("summary", {})
    ocr_summary = agent_outputs.get("document_intelligence", {})
    validation_summary = agent_outputs.get("validation_compliance", {}).get("summary", {})

    decision = evaluate(
        ocr_summary=ocr_summary,
        validation_summary=validation_summary,
        human_review_required=state.get("human_review_required", False),
        retry_count=state.get("retry_count", 0),
        intake_summary=intake_summary,
    )
    decision.audit_trail = build_audit_trail(decision, ocr_summary, validation_summary, intake_summary)
    return decision
