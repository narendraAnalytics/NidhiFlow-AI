from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.node_execution import NodeExecution
from app.models.workflow_execution import WorkflowExecution
from app.schemas.monitoring import NodeStat, WorkflowHealthResponse


def get_workflow_health(db: Session) -> WorkflowHealthResponse:
    executions = db.query(WorkflowExecution).all()
    node_executions = db.query(NodeExecution).all()

    total_executions = len(executions)
    if total_executions:
        success_count = sum(1 for e in executions if e.workflow_status == "Processing")
        human_review_count = sum(1 for e in executions if e.workflow_status == "Human Review")
        success_rate = success_count / total_executions
        human_review_rate = human_review_count / total_executions
        durations = [e.duration for e in executions if e.duration is not None]
        avg_duration_seconds = sum(durations) / len(durations) if durations else None
    else:
        success_rate = 0.0
        human_review_rate = 0.0
        avg_duration_seconds = None

    by_node: dict[str, list[NodeExecution]] = defaultdict(list)
    for node_exec in node_executions:
        by_node[node_exec.node_name].append(node_exec)

    node_stats = []
    for node_name, records in sorted(by_node.items()):
        durations = [r.duration for r in records if r.duration is not None]
        failures = [r for r in records if r.status == "failed"]
        failure_categories: dict[str, int] = defaultdict(int)
        for f in failures:
            if f.error_category:
                failure_categories[f.error_category] += 1

        node_stats.append(
            NodeStat(
                node_name=node_name,
                avg_duration_seconds=sum(durations) / len(durations) if durations else None,
                execution_count=len(records),
                failure_count=len(failures),
                failure_categories=dict(failure_categories),
            )
        )

    return WorkflowHealthResponse(
        total_executions=total_executions,
        success_rate=success_rate,
        human_review_rate=human_review_rate,
        avg_duration_seconds=avg_duration_seconds,
        node_stats=node_stats,
    )
