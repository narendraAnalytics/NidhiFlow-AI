from typing import Literal, Optional

from pydantic import BaseModel


class WorkflowEventRecord(BaseModel):
    stage: str
    event_type: str
    message: str


class OrchestrationDecision(BaseModel):
    decision: Literal["continue", "human_review", "retry", "stop"]
    decision_reason: str
    workflow_status: str
    error_category: Optional[str] = None
    audit_trail: list[WorkflowEventRecord] = []
