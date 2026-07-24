import logging
import random
import time
from typing import Callable

import httpx

logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def sleep_before_retry(attempt: int, base_backoff: float, max_backoff: float, response: httpx.Response | None) -> None:
    if response is not None:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                time.sleep(float(retry_after))
                return
            except ValueError:
                pass
    delay = min(base_backoff * (2**attempt), max_backoff)
    time.sleep(delay + random.uniform(0, delay * 0.25))


def request_with_retry(
    request_fn: Callable[[], httpx.Response],
    context: str,
    error_cls: type[Exception],
    max_attempts: int = 3,
    base_backoff: float = 1.0,
    max_backoff: float = 20.0,
) -> httpx.Response:
    """Runs an HTTP call with exponential-backoff retry for transient failures
    (timeouts, connection errors, HTTP 429/5xx). Non-retryable 4xx responses
    are returned immediately so the caller's own status check can surface
    them without a wasted retry. Shared by any client hitting the Sarvam API
    (Vision OCR and chat completions), which both need the same 429/5xx
    backoff behavior.
    """
    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        try:
            response = request_fn()
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            last_exc = exc
            if attempt == max_attempts - 1:
                raise error_cls(f"{context} failed after {max_attempts} attempts: {exc}") from exc
            logger.warning("%s network error (attempt %d/%d): %s", context, attempt + 1, max_attempts, exc)
            sleep_before_retry(attempt, base_backoff, max_backoff, None)
            continue

        if response.status_code in RETRYABLE_STATUS_CODES and attempt < max_attempts - 1:
            logger.warning(
                "%s returned status %d (attempt %d/%d), retrying",
                context,
                response.status_code,
                attempt + 1,
                max_attempts,
            )
            sleep_before_retry(attempt, base_backoff, max_backoff, response)
            continue

        return response

    raise error_cls(f"{context} failed after {max_attempts} attempts: {last_exc}")
