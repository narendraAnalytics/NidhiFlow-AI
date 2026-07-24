import re


def friendly_decision_message(message: str) -> str:
    """Softens the raw `decision=X reason=Y` audit-event string for human-facing
    display. Only affects display text — the underlying WorkflowEvent.message
    and every other consumer of the raw string is untouched.
    """
    if "reason=" not in message:
        return message
    reason = message.split("reason=", 1)[1]
    # Whole-reason replacements (no document names or other specifics carried
    # through to the UI) take priority over prefix replacements below.
    whole_replacements = [
        (
            "Required documents missing:",
            "A few more supporting documents are needed before this can be processed automatically.",
        ),
    ]
    for needle, friendly in whole_replacements:
        if reason.startswith(needle):
            return friendly

    prefix_replacements = [
        ("Some documents failed OCR parsing and retry budget exhausted", "Some documents could not be automatically read and require manual review"),
        ("Some documents failed OCR parsing; retry budget available", "Some documents could not be automatically read; the system will retry"),
        ("OCR failed for all documents; workflow cannot continue without extracted text", "None of the uploaded documents could be automatically read — manual review needed"),
        ("Validation failed cross-checks", "Some details could not be cross-verified"),
        ("Flagged for human review by an earlier workflow stage", "Flagged for a closer look by an earlier stage"),
    ]
    for needle, friendly in prefix_replacements:
        if reason.startswith(needle):
            reason = friendly + reason[len(needle):]
            break
    return reason


def friendly_workflow_event_description(event_type: str, message: str | None) -> str | None:
    """Maps a raw WorkflowEvent (event_type, message) pair — produced by
    pipeline_orchestrator/decision_engine.py's build_audit_trail — to a
    human-facing description for timeline/report display. The stored
    WorkflowEvent row is never modified; this only affects what gets shown.
    """
    if not message:
        return message

    if event_type in ("Intake Completed", "Intake Incomplete"):
        return (
            "Initial application check completed successfully."
            if "status=passed" in message
            else "Initial application check found a few items that need a closer look."
        )

    if event_type in ("OCR Completed", "OCR Failed"):
        return (
            "Documents were scanned successfully."
            if "status=failed" not in message
            else "Some documents could not be automatically scanned and need manual review."
        )

    if event_type == "Validation Completed":
        status_match = re.search(r"status=(\w+)", message)
        confidence_match = re.search(r"confidence=([\d.]+)", message)
        status = status_match.group(1) if status_match else None
        if status == "passed":
            base = "Document validation completed successfully."
        elif status == "warning":
            base = "Document validation completed with a few notes for the reviewer."
        else:
            base = "Document validation completed — some items need a closer look from the Branch Manager."
        if confidence_match:
            base += f" (Confidence: {round(float(confidence_match.group(1)) * 100)}%)"
        return base

    if event_type == "Pipeline Decision":
        return friendly_decision_message(message)

    if event_type == "Workflow Completed":
        status_map = {
            "Human Review": "Application sent to the Branch Manager for final review.",
            "Processing": "Application is proceeding automatically to the next stage.",
        }
        status_match = re.search(r"workflow_status=(.+)$", message)
        status = status_match.group(1) if status_match else None
        return status_map.get(status, message)

    return message
