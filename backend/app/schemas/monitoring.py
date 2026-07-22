from typing import Optional

from pydantic import BaseModel


class NodeStat(BaseModel):
    node_name: str
    avg_duration_seconds: Optional[float]
    execution_count: int
    failure_count: int
    failure_categories: dict[str, int]


class WorkflowHealthResponse(BaseModel):
    total_executions: int
    success_rate: float
    human_review_rate: float
    avg_duration_seconds: Optional[float]
    node_stats: list[NodeStat]
