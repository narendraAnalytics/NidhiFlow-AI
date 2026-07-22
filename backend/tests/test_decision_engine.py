from app.agents.pipeline_orchestrator.decision_engine import build_audit_trail, evaluate
from app.agents.pipeline_orchestrator.rules import (
    ERROR_HUMAN_REVIEW_REQUIRED,
    ERROR_MISSING_DOCUMENT,
    ERROR_OCR_ERROR,
    ERROR_VALIDATION_ERROR,
    MAX_RETRY_ATTEMPTS,
    WORKFLOW_STATUS_CONTINUE,
    WORKFLOW_STATUS_HUMAN_REVIEW,
)

PASSING_VALIDATION = {
    "validation_status": "passed",
    "confidence": 0.95,
    "missing_documents": [],
}
PARSED_OCR = {"status": "parsed"}


def test_ocr_failed_stops_workflow():
    decision = evaluate(
        ocr_summary={"status": "failed"},
        validation_summary=PASSING_VALIDATION,
        human_review_required=False,
        retry_count=0,
    )
    assert decision.decision == "stop"
    assert decision.workflow_status == WORKFLOW_STATUS_HUMAN_REVIEW
    assert decision.error_category == ERROR_OCR_ERROR


def test_missing_required_documents_triggers_human_review():
    decision = evaluate(
        ocr_summary=PARSED_OCR,
        validation_summary={**PASSING_VALIDATION, "missing_documents": ["Aadhaar"]},
        human_review_required=False,
        retry_count=0,
    )
    assert decision.decision == "human_review"
    assert decision.error_category == ERROR_MISSING_DOCUMENT


def test_validation_failed_triggers_human_review():
    decision = evaluate(
        ocr_summary=PARSED_OCR,
        validation_summary={**PASSING_VALIDATION, "validation_status": "failed"},
        human_review_required=False,
        retry_count=0,
    )
    assert decision.decision == "human_review"
    assert decision.error_category == ERROR_VALIDATION_ERROR


def test_confidence_below_threshold_triggers_human_review():
    decision = evaluate(
        ocr_summary=PARSED_OCR,
        validation_summary={**PASSING_VALIDATION, "confidence": 0.5},
        human_review_required=False,
        retry_count=0,
    )
    assert decision.decision == "human_review"
    assert decision.error_category == ERROR_HUMAN_REVIEW_REQUIRED


def test_partial_ocr_retries_within_budget():
    decision = evaluate(
        ocr_summary={"status": "partial"},
        validation_summary=PASSING_VALIDATION,
        human_review_required=False,
        retry_count=0,
    )
    assert decision.decision == "retry"
    assert decision.error_category == ERROR_OCR_ERROR


def test_partial_ocr_exhausted_retries_triggers_human_review():
    decision = evaluate(
        ocr_summary={"status": "partial"},
        validation_summary=PASSING_VALIDATION,
        human_review_required=False,
        retry_count=MAX_RETRY_ATTEMPTS,
    )
    assert decision.decision == "human_review"


def test_prior_human_review_flag_is_honored():
    decision = evaluate(
        ocr_summary=PARSED_OCR,
        validation_summary=PASSING_VALIDATION,
        human_review_required=True,
        retry_count=0,
    )
    assert decision.decision == "human_review"


def test_all_checks_passed_continues():
    decision = evaluate(
        ocr_summary=PARSED_OCR,
        validation_summary=PASSING_VALIDATION,
        human_review_required=False,
        retry_count=0,
    )
    assert decision.decision == "continue"
    assert decision.workflow_status == WORKFLOW_STATUS_CONTINUE
    assert decision.error_category is None


def test_build_audit_trail_has_four_events_in_order():
    decision = evaluate(
        ocr_summary=PARSED_OCR,
        validation_summary=PASSING_VALIDATION,
        human_review_required=False,
        retry_count=0,
    )
    trail = build_audit_trail(decision, PARSED_OCR, PASSING_VALIDATION)
    assert [e.event_type for e in trail] == [
        "OCR Completed",
        "Validation Completed",
        "Pipeline Decision",
        "Workflow Completed",
    ]
