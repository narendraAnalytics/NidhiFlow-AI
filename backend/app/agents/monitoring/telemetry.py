import functools
import time
from datetime import datetime, timezone
from typing import Callable

from app.agents.monitoring.schemas import NodeTelemetryRecord
from app.agents.state import LoanWorkflowState


def track_node(node_name: str, error_category: str) -> Callable[[Callable[[LoanWorkflowState], dict]], Callable[[LoanWorkflowState], dict]]:
    """Decorator factory applied at graph.py's add_node() call sites.

    Wraps a node function to record wall-clock duration and infer
    success/failure from whether the node appended to state['errors'].
    Does not touch the wrapped node's own return value other than
    appending a node_telemetry entry — purely additive.
    """

    # The literal string each node's own except block appends to state["errors"]
    # (see nodes.py) — used to distinguish a genuine unhandled exception from
    # a routine business-rule flag (e.g. "No documents attached at submission")
    # that also happens to append to the same errors list.
    exception_marker = f"{node_name}: unexpected error"

    def decorator(node_fn: Callable[[LoanWorkflowState], dict]) -> Callable[[LoanWorkflowState], dict]:
        @functools.wraps(node_fn)
        def wrapper(state: LoanWorkflowState) -> dict:
            started_at = datetime.now(timezone.utc)
            start_perf = time.perf_counter()
            new_errors = state.get("errors", [])

            result = node_fn(state)

            finished_at = datetime.now(timezone.utc)
            duration = time.perf_counter() - start_perf
            errors_after = result.get("errors", new_errors)
            last_error = errors_after[-1] if len(errors_after) > len(new_errors) else None

            failed = last_error == exception_marker
            record = NodeTelemetryRecord(
                node_name=node_name,
                status="failed" if failed else "completed",
                started_at=started_at.isoformat(),
                finished_at=finished_at.isoformat(),
                duration=duration,
                error_category=error_category if failed else None,
                error_message=last_error if failed else None,
                retry_attempt=state.get("retry_count", 0),
            )

            return {
                **result,
                "node_telemetry": [
                    *state.get("node_telemetry", []),
                    record.model_dump(mode="json"),
                ],
            }

        return wrapper

    return decorator
