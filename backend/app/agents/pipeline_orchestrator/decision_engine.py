from app.agents.pipeline_orchestrator.rules import (
    CONFIDENCE_THRESHOLD,
    ERROR_HUMAN_REVIEW_REQUIRED,
    ERROR_INTAKE_INCOMPLETE,
    ERROR_MISSING_DOCUMENT,
    ERROR_OCR_ERROR,
    ERROR_VALIDATION_ERROR,
    MAX_RETRY_ATTEMPTS,
    WORKFLOW_STATUS_CONTINUE,
    WORKFLOW_STATUS_HUMAN_REVIEW,
)
from app.agents.pipeline_orchestrator.schemas import OrchestrationDecision, WorkflowEventRecord


def evaluate(
    ocr_summary: dict,
    validation_summary: dict,
    human_review_required: bool,
    retry_count: int,
    intake_summary: dict | None = None,
) -> OrchestrationDecision:
    """Pure, deterministic decision matrix. No LLM calls, no DB reads.

    The orchestrator only ever routes to WORKFLOW_STATUS_CONTINUE (all clear)
    or WORKFLOW_STATUS_HUMAN_REVIEW (anything else, including unrecoverable
    failures) — it never decides APPROVED/REJECTED, since those are lending
    decisions reserved for a human underwriter.
    """
    ocr_status = ocr_summary.get("status", "parsed")
    validation_status = validation_summary.get("validation_status", "passed")
    confidence = validation_summary.get("confidence", 0.0)
    missing_documents = validation_summary.get("missing_documents", [])

    if ocr_status == "failed":
        return OrchestrationDecision(
            decision="stop",
            decision_reason="OCR failed for all documents; workflow cannot continue without extracted text",
            workflow_status=WORKFLOW_STATUS_HUMAN_REVIEW,
            error_category=ERROR_OCR_ERROR,
        )

    if missing_documents:
        return OrchestrationDecision(
            decision="human_review",
            decision_reason=f"Required documents missing: {', '.join(missing_documents)}",
            workflow_status=WORKFLOW_STATUS_HUMAN_REVIEW,
            error_category=ERROR_MISSING_DOCUMENT,
        )

    if validation_status == "failed":
        return OrchestrationDecision(
            decision="human_review",
            decision_reason="Validation failed cross-checks (field mismatches or affordability check)",
            workflow_status=WORKFLOW_STATUS_HUMAN_REVIEW,
            error_category=ERROR_VALIDATION_ERROR,
        )

    if confidence < CONFIDENCE_THRESHOLD:
        return OrchestrationDecision(
            decision="human_review",
            decision_reason=f"Validation confidence {confidence:.2f} below threshold {CONFIDENCE_THRESHOLD:.2f}",
            workflow_status=WORKFLOW_STATUS_HUMAN_REVIEW,
            error_category=ERROR_HUMAN_REVIEW_REQUIRED,
        )

    if ocr_status == "partial":
        if retry_count < MAX_RETRY_ATTEMPTS:
            return OrchestrationDecision(
                decision="retry",
                decision_reason=f"Some documents failed OCR parsing; retry budget available (retry_count={retry_count})",
                workflow_status=WORKFLOW_STATUS_HUMAN_REVIEW,
                error_category=ERROR_OCR_ERROR,
            )
        return OrchestrationDecision(
            decision="human_review",
            decision_reason="Some documents failed OCR parsing and retry budget exhausted",
            workflow_status=WORKFLOW_STATUS_HUMAN_REVIEW,
            error_category=ERROR_OCR_ERROR,
        )

    if human_review_required:
        intake_summary = intake_summary or {}
        intake_missing_documents = intake_summary.get("missing_documents", [])
        intake_missing_form_fields = intake_summary.get("missing_form_fields", [])
        if intake_summary.get("status") == "failed" and (intake_missing_documents or intake_missing_form_fields):
            reasons = []
            if intake_missing_documents:
                reasons.append(f"missing documents: {', '.join(intake_missing_documents)}")
            if intake_missing_form_fields:
                reasons.append(f"missing form fields: {', '.join(intake_missing_form_fields)}")
            return OrchestrationDecision(
                decision="human_review",
                decision_reason=f"Intake incomplete ({'; '.join(reasons)})",
                workflow_status=WORKFLOW_STATUS_HUMAN_REVIEW,
                error_category=ERROR_INTAKE_INCOMPLETE,
            )

        return OrchestrationDecision(
            decision="human_review",
            decision_reason="Flagged for human review by an earlier workflow stage",
            workflow_status=WORKFLOW_STATUS_HUMAN_REVIEW,
            error_category=ERROR_HUMAN_REVIEW_REQUIRED,
        )

    return OrchestrationDecision(
        decision="continue",
        decision_reason="All checks passed: documents complete, validation passed, confidence above threshold",
        workflow_status=WORKFLOW_STATUS_CONTINUE,
    )


def build_audit_trail(
    decision: OrchestrationDecision,
    ocr_summary: dict,
    validation_summary: dict,
    intake_summary: dict | None = None,
) -> list[WorkflowEventRecord]:
    ocr_status = ocr_summary.get("status", "parsed")
    validation_status = validation_summary.get("validation_status", "passed")
    intake_summary = intake_summary or {}
    intake_status = intake_summary.get("status", "passed")

    return [
        WorkflowEventRecord(
            stage="intake_supervisor",
            event_type="Intake Completed" if intake_status == "passed" else "Intake Incomplete",
            message=f"intake_supervisor status={intake_status}",
        ),
        WorkflowEventRecord(
            stage="document_intelligence",
            event_type="OCR Completed" if ocr_status != "failed" else "OCR Failed",
            message=f"document_intelligence status={ocr_status}",
        ),
        WorkflowEventRecord(
            stage="validation_compliance",
            event_type="Validation Completed",
            message=f"validation_compliance status={validation_status} confidence={validation_summary.get('confidence')}",
        ),
        WorkflowEventRecord(
            stage="pipeline_orchestrator",
            event_type="Pipeline Decision",
            message=f"decision={decision.decision} reason={decision.decision_reason}",
        ),
        WorkflowEventRecord(
            stage="pipeline_orchestrator",
            event_type="Workflow Completed",
            message=f"workflow_status={decision.workflow_status}",
        ),
    ]
