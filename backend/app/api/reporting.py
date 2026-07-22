import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.reporting import (
    AuditTrailResponse,
    HumanReviewAnalyticsResponse,
    LoanTimelineResponse,
    ProcessingTimelineResponse,
    RetryAnalyticsResponse,
)
from app.services.reporting_service import (
    LoanNotFoundError,
    get_audit_trail,
    get_human_review_analytics,
    get_loan_timeline,
    get_processing_timelines,
    get_retry_analytics,
)

router = APIRouter(prefix="/reporting", tags=["reporting"])


@router.get("/loans/{loan_id}/timeline", response_model=LoanTimelineResponse)
def get_loan_timeline_route(loan_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return get_loan_timeline(db, loan_id)
    except LoanNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/audit-trail", response_model=AuditTrailResponse)
def get_audit_trail_route(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    loan_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
):
    return get_audit_trail(db, limit=limit, offset=offset, loan_id=loan_id)


@router.get("/retry-analytics", response_model=RetryAnalyticsResponse)
def get_retry_analytics_route(db: Session = Depends(get_db)):
    return get_retry_analytics(db)


@router.get("/human-review-analytics", response_model=HumanReviewAnalyticsResponse)
def get_human_review_analytics_route(db: Session = Depends(get_db)):
    return get_human_review_analytics(db)


@router.get("/processing-timelines", response_model=ProcessingTimelineResponse)
def get_processing_timelines_route(db: Session = Depends(get_db)):
    return get_processing_timelines(db)
