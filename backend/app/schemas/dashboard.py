import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.enums import LoanStatus, LoanType


class PipelineStageCount(BaseModel):
    stage: str
    count: int


class StatusDistributionSlice(BaseModel):
    status: str
    count: int
    percentage: float


class TrendPoint(BaseModel):
    date: date
    applications: int
    approved: int


class RecentApplicationItem(BaseModel):
    id: uuid.UUID
    loan_type: LoanType
    customer_name: str
    status: LoanStatus
    requested_amount: Decimal
    created_at: datetime


class DashboardStatsResponse(BaseModel):
    total_applications: int
    in_process: int
    approved: int
    avg_processing_days: Optional[float]
    success_rate: float
    total_disbursed_amount: Decimal
    pipeline: list[PipelineStageCount]
    conversion_rate: float
    status_distribution: list[StatusDistributionSlice]
    trend: list[TrendPoint]
    recent: list[RecentApplicationItem]
