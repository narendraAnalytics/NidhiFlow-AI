from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.nodes import document_intelligence_node, intake_supervisor_node
from app.agents.state import LoanWorkflowState


def build_loan_workflow_graph() -> CompiledStateGraph:
    builder = StateGraph(LoanWorkflowState)
    builder.add_node("intake_supervisor", intake_supervisor_node)
    builder.add_node("document_intelligence", document_intelligence_node)
    builder.add_edge(START, "intake_supervisor")
    builder.add_edge("intake_supervisor", "document_intelligence")
    builder.add_edge("document_intelligence", END)
    return builder.compile()


# Compiled once at import time: compile() captures no per-request state
# (no DB session, no checkpointer), so sharing this across requests is safe.
loan_workflow_graph = build_loan_workflow_graph()
