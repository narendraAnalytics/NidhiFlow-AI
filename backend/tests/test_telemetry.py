from app.agents.monitoring.telemetry import track_node


def _base_state(**overrides) -> dict:
    state = {
        "loan_application_id": "loan-1",
        "documents": [],
        "errors": [],
        "node_telemetry": [],
        "retry_count": 0,
    }
    state.update(overrides)
    return state


def test_track_node_marks_completed_when_no_new_errors():
    def fake_node(state):
        return {"current_stage": "fake_node"}

    wrapped = track_node("fake_node", "SYSTEM_ERROR")(fake_node)
    result = wrapped(_base_state())

    telemetry = result["node_telemetry"]
    assert len(telemetry) == 1
    assert telemetry[0]["node_name"] == "fake_node"
    assert telemetry[0]["status"] == "completed"
    assert telemetry[0]["error_category"] is None
    assert telemetry[0]["duration"] >= 0


def test_track_node_marks_failed_on_unexpected_error_marker():
    def fake_node(state):
        return {"errors": [*state.get("errors", []), "fake_node: unexpected error"]}

    wrapped = track_node("fake_node", "OCR_ERROR")(fake_node)
    result = wrapped(_base_state())

    telemetry = result["node_telemetry"]
    assert telemetry[0]["status"] == "failed"
    assert telemetry[0]["error_category"] == "OCR_ERROR"
    assert telemetry[0]["error_message"] == "fake_node: unexpected error"


def test_track_node_does_not_flag_business_rule_errors_as_failed():
    def fake_node(state):
        return {"errors": [*state.get("errors", []), "No documents attached at submission"]}

    wrapped = track_node("fake_node", "OCR_ERROR")(fake_node)
    result = wrapped(_base_state())

    telemetry = result["node_telemetry"]
    assert telemetry[0]["status"] == "completed"
    assert telemetry[0]["error_category"] is None


def test_track_node_preserves_prior_telemetry_entries():
    def fake_node(state):
        return {}

    wrapped = track_node("second_node", "SYSTEM_ERROR")(fake_node)
    prior = _base_state(node_telemetry=[{"node_name": "first_node", "status": "completed"}])
    result = wrapped(prior)

    assert [t["node_name"] for t in result["node_telemetry"]] == ["first_node", "second_node"]


def test_track_node_records_retry_attempt_from_state():
    def fake_node(state):
        return {}

    wrapped = track_node("fake_node", "SYSTEM_ERROR")(fake_node)
    result = wrapped(_base_state(retry_count=2))

    assert result["node_telemetry"][0]["retry_attempt"] == 2


def test_track_node_does_not_mutate_input_state_errors():
    def fake_node(state):
        return {"errors": [*state.get("errors", []), "boom"]}

    wrapped = track_node("fake_node", "SYSTEM_ERROR")(fake_node)
    state = _base_state()
    wrapped(state)

    assert state["errors"] == []
