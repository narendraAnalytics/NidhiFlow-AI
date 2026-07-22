import uuid
from typing import Optional, TypedDict


class LoanWorkflowState(TypedDict):
    loan_application_id: uuid.UUID
    customer_id: uuid.UUID
    loan_status: str
    documents: list[dict]
    customer_profile: dict
    loan_details: dict
    current_stage: Optional[str]
    human_review_required: bool
    agent_outputs: dict
    errors: list[str]
    next_stage: Optional[str]
    workflow_status: str
    retry_count: int
    decision: Optional[str]
    decision_reason: Optional[str]
    pipeline_completed: bool
    pipeline_started_at: Optional[str]
    pipeline_finished_at: Optional[str]
    node_telemetry: list[dict]
