from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.models.enums import LoanStatus
from app.models.loan_application import LoanApplication
from app.schemas.dashboard import (
    DashboardStatsResponse,
    PipelineStageCount,
    RecentApplicationItem,
    StatusDistributionSlice,
    TrendPoint,
)

IN_PROCESS_STATUSES = {
    LoanStatus.DOCUMENTS_UPLOADED,
    LoanStatus.PROCESSING,
    LoanStatus.HUMAN_REVIEW,
}
APPROVED_STATUSES = {LoanStatus.APPROVED, LoanStatus.COMPLETED}
TERMINAL_STATUSES = {LoanStatus.APPROVED, LoanStatus.REJECTED, LoanStatus.COMPLETED}

TREND_WINDOW_DAYS = 30
RECENT_LIMIT = 8


def get_dashboard_stats(db: Session) -> DashboardStatsResponse:
    applications = (
        db.query(LoanApplication)
        .options(joinedload(LoanApplication.customer))
        .all()
    )

    total_applications = len(applications)
    in_process = sum(1 for a in applications if a.status in IN_PROCESS_STATUSES)
    approved = sum(1 for a in applications if a.status in APPROVED_STATUSES)
    completed = sum(1 for a in applications if a.status == LoanStatus.COMPLETED)
    rejected = sum(1 for a in applications if a.status == LoanStatus.REJECTED)

    terminal = [a for a in applications if a.status in TERMINAL_STATUSES]
    if terminal:
        avg_processing_days = sum(
            (a.updated_at - a.created_at).total_seconds() / 86400 for a in terminal
        ) / len(terminal)
    else:
        avg_processing_days = None

    success_rate = (approved / len(terminal)) if terminal else 0.0
    conversion_rate = (completed / total_applications) if total_applications else 0.0

    total_disbursed_amount = sum(
        (a.requested_amount for a in applications if a.status in APPROVED_STATUSES),
        start=Decimal("0"),
    )

    pipeline = [
        PipelineStageCount(stage="Intake", count=total_applications),
        PipelineStageCount(
            stage="Validation",
            count=sum(1 for a in applications if a.status != LoanStatus.DRAFT),
        ),
        PipelineStageCount(
            stage="Underwriting",
            count=sum(
                1
                for a in applications
                if a.status
                in {
                    LoanStatus.PROCESSING,
                    LoanStatus.HUMAN_REVIEW,
                    LoanStatus.APPROVED,
                    LoanStatus.REJECTED,
                    LoanStatus.COMPLETED,
                }
            ),
        ),
        PipelineStageCount(
            stage="Approval",
            count=sum(
                1
                for a in applications
                if a.status in {LoanStatus.APPROVED, LoanStatus.REJECTED, LoanStatus.COMPLETED}
            ),
        ),
        PipelineStageCount(stage="Disbursed", count=completed),
    ]

    draft_count = sum(1 for a in applications if a.status == LoanStatus.DRAFT)
    approved_only_count = sum(1 for a in applications if a.status == LoanStatus.APPROVED)
    distribution_counts = [
        ("Draft", draft_count),
        ("In Process", in_process),
        ("Approved", approved_only_count),
        ("Disbursed", completed),
        ("Rejected", rejected),
    ]
    status_distribution = [
        StatusDistributionSlice(
            status=label,
            count=count,
            percentage=round((count / total_applications) * 100, 1) if total_applications else 0.0,
        )
        for label, count in distribution_counts
        if count > 0
    ]

    trend = _build_trend(applications)

    recent = [
        RecentApplicationItem(
            id=a.id,
            loan_type=a.loan_type,
            customer_name=a.customer.full_name if a.customer else "Unknown",
            status=a.status,
            requested_amount=a.requested_amount,
            created_at=a.created_at,
        )
        for a in sorted(applications, key=lambda a: a.created_at, reverse=True)[:RECENT_LIMIT]
    ]

    return DashboardStatsResponse(
        total_applications=total_applications,
        in_process=in_process,
        approved=approved,
        avg_processing_days=avg_processing_days,
        success_rate=success_rate,
        total_disbursed_amount=total_disbursed_amount,
        pipeline=pipeline,
        conversion_rate=conversion_rate,
        status_distribution=status_distribution,
        trend=trend,
        recent=recent,
    )


def _build_trend(applications: list[LoanApplication]) -> list[TrendPoint]:
    today = date.today()
    window_start = today - timedelta(days=TREND_WINDOW_DAYS - 1)

    applications_by_day: dict[date, int] = defaultdict(int)
    approved_by_day: dict[date, int] = defaultdict(int)

    for a in applications:
        created_day = a.created_at.date()
        if created_day >= window_start:
            applications_by_day[created_day] += 1
        if a.status in APPROVED_STATUSES:
            approved_day = a.updated_at.date()
            if approved_day >= window_start:
                approved_by_day[approved_day] += 1

    trend: list[TrendPoint] = []
    day = window_start
    while day <= today:
        trend.append(
            TrendPoint(
                date=day,
                applications=applications_by_day.get(day, 0),
                approved=approved_by_day.get(day, 0),
            )
        )
        day += timedelta(days=1)
    return trend
