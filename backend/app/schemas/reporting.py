import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel


class LoanTimelineEvent(BaseModel):
    timestamp: datetime
    category: Literal["status_change", "workflow_event", "node_execution"]
    title: str
    description: Optional[str]
    metadata: dict


class LoanSummary(BaseModel):
    loan_type: str
    requested_amount: Decimal
    status: str
    created_at: datetime


class CustomerSummary(BaseModel):
    full_name: str


class ValidationSummary(BaseModel):
    validation_status: str
    confidence: float
    missing_documents: list[str]
    field_mismatches: list[str]


class LoanTimelineResponse(BaseModel):
    loan_application_id: uuid.UUID
    loan: LoanSummary
    customer: CustomerSummary
    validation_summary: Optional[ValidationSummary]
    events: list[LoanTimelineEvent]


class AuditTrailEntry(BaseModel):
    loan_application_id: uuid.UUID
    customer_name: str
    previous_status: Optional[str]
    new_status: str
    changed_by: Optional[str]
    notes: Optional[str]
    changed_at: datetime


class AuditTrailResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[AuditTrailEntry]


class NodeRetryStat(BaseModel):
    node_name: str
    avg_retry_attempts: float
    max_retry_attempts: int


class RetryAnalyticsResponse(BaseModel):
    total_workflows: int
    workflows_with_retries: int
    retry_rate: float
    avg_retry_count: float
    node_retry_stats: list[NodeRetryStat]


class HumanReviewAnalyticsResponse(BaseModel):
    current_queue_size: int
    total_human_review_count: int
    human_review_rate: float
    reason_breakdown: dict[str, int]
    avg_time_in_queue_hours: Optional[float]


class StageDuration(BaseModel):
    status: str
    avg_duration_hours: float
    sample_size: int


class ProcessingTimelineResponse(BaseModel):
    stage_durations: list[StageDuration]
