import logging

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import RetryPolicy
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.agents.monitoring.rules import NODE_ERROR_CATEGORY
from app.agents.monitoring.telemetry import track_node
from app.agents.nodes import (
    document_intelligence_node,
    intake_supervisor_node,
    pipeline_orchestrator_node,
    validation_compliance_node,
)
from app.agents.state import LoanWorkflowState
from app.core.config import DATABASE_URL

logger = logging.getLogger(__name__)


def _build_checkpointer() -> PostgresSaver:
    pool = ConnectionPool(
        conninfo=DATABASE_URL,
        kwargs={"autocommit": True, "row_factory": dict_row},
        min_size=1,
        max_size=5,
        open=True,
    )
    checkpointer = PostgresSaver(pool)
    checkpointer.setup()
    logger.info("PostgresSaver checkpointer initialized")
    return checkpointer


def build_loan_workflow_graph() -> CompiledStateGraph:
    builder = StateGraph(LoanWorkflowState)
    builder.add_node("intake_supervisor", track_node("intake_supervisor", NODE_ERROR_CATEGORY["intake_supervisor"])(intake_supervisor_node))
    builder.add_node(
        "document_intelligence",
        track_node("document_intelligence", NODE_ERROR_CATEGORY["document_intelligence"])(document_intelligence_node),
        retry_policy=RetryPolicy(max_attempts=2),
    )
    builder.add_node(
        "validation_compliance",
        track_node("validation_compliance", NODE_ERROR_CATEGORY["validation_compliance"])(validation_compliance_node),
        retry_policy=RetryPolicy(max_attempts=2),
    )
    builder.add_node("pipeline_orchestrator", track_node("pipeline_orchestrator", NODE_ERROR_CATEGORY["pipeline_orchestrator"])(pipeline_orchestrator_node))
    builder.add_edge(START, "intake_supervisor")
    builder.add_edge("intake_supervisor", "document_intelligence")
    builder.add_edge("document_intelligence", "validation_compliance")
    builder.add_edge("validation_compliance", "pipeline_orchestrator")
    builder.add_edge("pipeline_orchestrator", END)
    return builder.compile(checkpointer=_build_checkpointer())


# Compiled once at import time. Unlike Steps 1-6, this now holds a live
# psycopg connection pool (Postgres-backed checkpointer) for the process
# lifetime — the Cloud SQL Auth Proxy must be running before this module
# can be imported.
loan_workflow_graph = build_loan_workflow_graph()
