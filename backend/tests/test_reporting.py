import uuid
from datetime import datetime, timedelta, timezone

from app.services.reporting_service import _parse_decision_from_message, compute_stage_durations


def _dt(hours_from_now: int) -> datetime:
    return datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=hours_from_now)


def test_compute_stage_durations_single_loan():
    loan_id = uuid.uuid4()
    history = {
        loan_id: [
            ("Documents Uploaded", _dt(0)),
            ("Processing", _dt(2)),
            ("Human Review", _dt(5)),
        ]
    }
    stats = compute_stage_durations(history)
    by_status = {s.status: s for s in stats}

    assert by_status["Documents Uploaded"].avg_duration_hours == 2
    assert by_status["Documents Uploaded"].sample_size == 1
    assert by_status["Processing"].avg_duration_hours == 3
    assert by_status["Processing"].sample_size == 1
    assert "Human Review" not in by_status  # last status has no "time spent" yet


def test_compute_stage_durations_averages_across_loans():
    loan_a, loan_b = uuid.uuid4(), uuid.uuid4()
    history = {
        loan_a: [("Documents Uploaded", _dt(0)), ("Processing", _dt(2))],
        loan_b: [("Documents Uploaded", _dt(0)), ("Processing", _dt(4))],
    }
    stats = compute_stage_durations(history)
    by_status = {s.status: s for s in stats}

    assert by_status["Documents Uploaded"].avg_duration_hours == 3
    assert by_status["Documents Uploaded"].sample_size == 2


def test_compute_stage_durations_ignores_single_transition_loans():
    loan_id = uuid.uuid4()
    history = {loan_id: [("Documents Uploaded", _dt(0))]}
    stats = compute_stage_durations(history)
    assert stats == []


def test_parse_decision_from_message():
    assert _parse_decision_from_message("decision=human_review reason=Required documents missing: PAN Card") == "human_review"
    assert _parse_decision_from_message("decision=continue reason=All checks passed") == "continue"


def test_parse_decision_from_message_handles_missing_or_malformed():
    assert _parse_decision_from_message(None) is None
    assert _parse_decision_from_message("") is None
    assert _parse_decision_from_message("some unrelated message") is None
