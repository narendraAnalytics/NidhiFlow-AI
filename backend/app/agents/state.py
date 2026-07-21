import uuid
from typing import Optional, TypedDict


class LoanWorkflowState(TypedDict):
    loan_application_id: uuid.UUID
    customer_id: uuid.UUID
    loan_status: str
    documents: list[dict]
    current_stage: Optional[str]
    human_review_required: bool
    agent_outputs: dict
    errors: list[str]
