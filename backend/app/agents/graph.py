from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import RetryPolicy

from app.agents.nodes import (
    document_intelligence_node,
    intake_supervisor_node,
    pipeline_orchestrator_node,
    validation_compliance_node,
)
from app.agents.state import LoanWorkflowState


def build_loan_workflow_graph() -> CompiledStateGraph:
    builder = StateGraph(LoanWorkflowState)
    builder.add_node("intake_supervisor", intake_supervisor_node)
    builder.add_node(
        "document_intelligence",
        document_intelligence_node,
        retry_policy=RetryPolicy(max_attempts=2),
    )
    builder.add_node(
        "validation_compliance",
        validation_compliance_node,
        retry_policy=RetryPolicy(max_attempts=2),
    )
    builder.add_node("pipeline_orchestrator", pipeline_orchestrator_node)
    builder.add_edge(START, "intake_supervisor")
    builder.add_edge("intake_supervisor", "document_intelligence")
    builder.add_edge("document_intelligence", "validation_compliance")
    builder.add_edge("validation_compliance", "pipeline_orchestrator")
    builder.add_edge("pipeline_orchestrator", END)
    return builder.compile()


# Compiled once at import time: compile() captures no per-request state
# (no DB session, no checkpointer), so sharing this across requests is safe.
loan_workflow_graph = build_loan_workflow_graph()
