import uuid
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.enums import LoanStatus
from app.models.loan_application import LoanApplication
from app.models.loan_status_history import LoanStatusHistory
from app.models.loan_validation_summary import LoanValidationSummary
from app.models.node_execution import NodeExecution
from app.models.workflow_event import WorkflowEvent
from app.models.workflow_execution import WorkflowExecution
from app.schemas.reporting import (
    AuditTrailEntry,
    AuditTrailResponse,
    CustomerSummary,
    HumanReviewAnalyticsResponse,
    LoanSummary,
    LoanTimelineEvent,
    LoanTimelineResponse,
    NodeRetryStat,
    ProcessingTimelineResponse,
    RetryAnalyticsResponse,
    StageDuration,
    ValidationSummary,
)
from app.utils.friendly_messages import friendly_workflow_event_description


class LoanNotFoundError(Exception):
    pass


def get_loan_timeline(db: Session, loan_id: uuid.UUID) -> LoanTimelineResponse:
    loan = db.query(LoanApplication).filter(LoanApplication.id == loan_id).first()
    if loan is None:
        raise LoanNotFoundError(f"Loan application {loan_id} not found")

    customer = db.query(Customer).filter(Customer.id == loan.customer_id).first()
    validation_summary_row = (
        db.query(LoanValidationSummary)
        .filter(LoanValidationSummary.loan_application_id == loan_id)
        .order_by(LoanValidationSummary.created_at.desc())
        .first()
    )

    status_history = (
        db.query(LoanStatusHistory)
        .filter(LoanStatusHistory.loan_application_id == loan_id)
        .order_by(LoanStatusHistory.changed_at)
        .all()
    )
    execution_ids = [
        e.id
        for e in db.query(WorkflowExecution.id)
        .filter(WorkflowExecution.loan_application_id == loan_id)
        .all()
    ]

    events: list[WorkflowEvent] = []
    node_execs: list[NodeExecution] = []
    if execution_ids:
        events = (
            db.query(WorkflowEvent)
            .filter(WorkflowEvent.workflow_execution_id.in_(execution_ids))
            .order_by(WorkflowEvent.created_at)
            .all()
        )
        node_execs = (
            db.query(NodeExecution)
            .filter(NodeExecution.workflow_execution_id.in_(execution_ids))
            .order_by(NodeExecution.finished_at)
            .all()
        )

    timeline: list[LoanTimelineEvent] = []
    for h in status_history:
        timeline.append(
            LoanTimelineEvent(
                timestamp=h.changed_at,
                category="status_change",
                title=f"{h.previous_status.value if h.previous_status else 'None'} -> {h.new_status.value}",
                description=h.notes,
                metadata={"changed_by": h.changed_by},
            )
        )
    for e in events:
        timeline.append(
            LoanTimelineEvent(
                timestamp=e.created_at,
                category="workflow_event",
                title=e.event_type,
                description=friendly_workflow_event_description(e.event_type, e.message),
                metadata={"stage": e.stage},
            )
        )
    for n in node_execs:
        timeline.append(
            LoanTimelineEvent(
                timestamp=n.finished_at or n.created_at,
                category="node_execution",
                title=f"{n.node_name}: {n.status}",
                description=n.error_message,
                metadata={
                    "started_at": n.started_at.isoformat() if n.started_at else None,
                    "duration": n.duration,
                    "error_category": n.error_category,
                    "retry_attempt": n.retry_attempt,
                },
            )
        )

    timeline.sort(key=lambda ev: ev.timestamp)

    return LoanTimelineResponse(
        loan_application_id=loan_id,
        loan=LoanSummary(
            loan_type=loan.loan_type.value,
            requested_amount=loan.requested_amount,
            status=loan.status.value,
            created_at=loan.created_at,
        ),
        customer=CustomerSummary(full_name=customer.full_name if customer else "Unknown"),
        validation_summary=ValidationSummary(
            validation_status=validation_summary_row.validation_status,
            confidence=validation_summary_row.confidence,
            missing_documents=validation_summary_row.missing_documents,
            field_mismatches=validation_summary_row.field_mismatches,
        )
        if validation_summary_row
        else None,
        events=timeline,
    )


def get_audit_trail(
    db: Session, limit: int = 50, offset: int = 0, loan_id: uuid.UUID | None = None
) -> AuditTrailResponse:
    query = (
        db.query(LoanStatusHistory, Customer.full_name)
        .join(LoanApplication, LoanStatusHistory.loan_application_id == LoanApplication.id)
        .join(Customer, LoanApplication.customer_id == Customer.id)
    )
    if loan_id is not None:
        query = query.filter(LoanStatusHistory.loan_application_id == loan_id)

    total = query.count()
    rows = (
        query.order_by(LoanStatusHistory.changed_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    items = [
        AuditTrailEntry(
            loan_application_id=history.loan_application_id,
            customer_name=full_name,
            previous_status=history.previous_status.value if history.previous_status else None,
            new_status=history.new_status.value,
            changed_by=history.changed_by,
            notes=history.notes,
            changed_at=history.changed_at,
        )
        for history, full_name in rows
    ]
    return AuditTrailResponse(total=total, limit=limit, offset=offset, items=items)


def get_retry_analytics(db: Session) -> RetryAnalyticsResponse:
    executions = db.query(WorkflowExecution).all()
    total_workflows = len(executions)
    with_retries = [e for e in executions if (e.retry_count or 0) > 0]
    retry_rate = len(with_retries) / total_workflows if total_workflows else 0.0
    avg_retry_count = (
        sum(e.retry_count or 0 for e in executions) / total_workflows if total_workflows else 0.0
    )

    node_execs = db.query(NodeExecution).all()
    attempts_by_node: dict[str, list[int]] = defaultdict(list)
    for n in node_execs:
        attempts_by_node[n.node_name].append(n.retry_attempt or 0)

    node_retry_stats = [
        NodeRetryStat(
            node_name=name,
            avg_retry_attempts=sum(attempts) / len(attempts),
            max_retry_attempts=max(attempts),
        )
        for name, attempts in sorted(attempts_by_node.items())
    ]

    return RetryAnalyticsResponse(
        total_workflows=total_workflows,
        workflows_with_retries=len(with_retries),
        retry_rate=retry_rate,
        avg_retry_count=avg_retry_count,
        node_retry_stats=node_retry_stats,
    )


def _parse_decision_from_message(message: str | None) -> str | None:
    """WorkflowEvent messages for event_type="Pipeline Decision" are written
    by decision_engine.build_audit_trail() as f"decision={decision} reason={reason}"
    (see pipeline_orchestrator/decision_engine.py). Nothing persists the
    OrchestrationDecision's structured fields directly, so this is the only
    way to recover the decision type from stored data without a schema change.
    """
    if not message or "decision=" not in message:
        return None
    after = message.split("decision=", 1)[1]
    return after.split(" reason=", 1)[0].strip() or None


def get_human_review_analytics(db: Session) -> HumanReviewAnalyticsResponse:
    current_queue_size = (
        db.query(LoanApplication).filter(LoanApplication.status == LoanStatus.HUMAN_REVIEW).count()
    )

    executions = db.query(WorkflowExecution).all()
    total_workflows = len(executions)
    human_review_count = sum(1 for e in executions if e.workflow_status == "Human Review")
    human_review_rate = human_review_count / total_workflows if total_workflows else 0.0

    decision_events = (
        db.query(WorkflowEvent).filter(WorkflowEvent.event_type == "Pipeline Decision").all()
    )
    reason_breakdown: dict[str, int] = defaultdict(int)
    for ev in decision_events:
        decision = _parse_decision_from_message(ev.message)
        if decision:
            reason_breakdown[decision] += 1

    now = datetime.now(timezone.utc)
    queue_durations_hours: list[float] = []
    human_review_loans = (
        db.query(LoanApplication).filter(LoanApplication.status == LoanStatus.HUMAN_REVIEW).all()
    )
    for loan in human_review_loans:
        latest_transition = (
            db.query(LoanStatusHistory)
            .filter(
                LoanStatusHistory.loan_application_id == loan.id,
                LoanStatusHistory.new_status == LoanStatus.HUMAN_REVIEW,
            )
            .order_by(LoanStatusHistory.changed_at.desc())
            .first()
        )
        if latest_transition:
            queue_durations_hours.append((now - latest_transition.changed_at).total_seconds() / 3600)

    avg_time_in_queue_hours = (
        sum(queue_durations_hours) / len(queue_durations_hours) if queue_durations_hours else None
    )

    return HumanReviewAnalyticsResponse(
        current_queue_size=current_queue_size,
        total_human_review_count=human_review_count,
        human_review_rate=human_review_rate,
        reason_breakdown=dict(reason_breakdown),
        avg_time_in_queue_hours=avg_time_in_queue_hours,
    )


def compute_stage_durations(
    history_by_loan: dict[uuid.UUID, list[tuple[str, datetime]]],
) -> list[StageDuration]:
    """Pure function: history_by_loan maps loan_id -> [(status_value, arrived_at), ...]
    sorted ascending by arrived_at. For each consecutive pair, the time between
    them is how long the loan spent in the *earlier* status before transitioning.
    """
    durations_by_status: dict[str, list[float]] = defaultdict(list)
    for transitions in history_by_loan.values():
        for i in range(1, len(transitions)):
            prev_status, prev_at = transitions[i - 1]
            _, next_at = transitions[i]
            hours = (next_at - prev_at).total_seconds() / 3600
            durations_by_status[prev_status].append(hours)

    return [
        StageDuration(status=status, avg_duration_hours=sum(vals) / len(vals), sample_size=len(vals))
        for status, vals in sorted(durations_by_status.items())
    ]


def get_processing_timelines(db: Session) -> ProcessingTimelineResponse:
    rows = (
        db.query(LoanStatusHistory)
        .order_by(LoanStatusHistory.loan_application_id, LoanStatusHistory.changed_at)
        .all()
    )
    history_by_loan: dict[uuid.UUID, list[tuple[str, datetime]]] = defaultdict(list)
    for row in rows:
        history_by_loan[row.loan_application_id].append((row.new_status.value, row.changed_at))

    return ProcessingTimelineResponse(stage_durations=compute_stage_durations(history_by_loan))
