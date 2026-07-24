import logging
import time

import httpx

from app.core.config import (
    SARVAM_API_KEY,
    SARVAM_BASE_URL,
    SARVAM_POLL_INTERVAL_SECONDS,
    SARVAM_POLL_TIMEOUT_SECONDS,
    SARVAM_VISION_LANGUAGE,
    SARVAM_VISION_OUTPUT_FORMAT,
)
from app.utils.http_retry import request_with_retry

logger = logging.getLogger(__name__)

JOB_BASE_PATH = "/doc-digitization/job/v1"

MAX_ATTEMPTS = 3


class SarvamVisionError(Exception):
    pass


def _request_with_retry(request_fn, context: str) -> httpx.Response:
    return request_with_retry(request_fn, f"Sarvam {context}", SarvamVisionError, max_attempts=MAX_ATTEMPTS)


def _raise_for_status(response: httpx.Response, context: str) -> None:
    if response.status_code >= 400:
        raise SarvamVisionError(
            f"Sarvam {context} failed with status {response.status_code}: {response.text}"
        )


class SarvamVisionClient:
    def __init__(self) -> None:
        self._client = httpx.Client(
            base_url=SARVAM_BASE_URL,
            headers={"api-subscription-key": SARVAM_API_KEY},
            timeout=30.0,
        )

    def create_document_job(self, language: str | None = None, output_format: str | None = None) -> dict:
        response = _request_with_retry(
            lambda: self._client.post(
                f"{JOB_BASE_PATH}",
                json={
                    "job_parameters": {
                        "language": language or SARVAM_VISION_LANGUAGE,
                        "output_format": output_format or SARVAM_VISION_OUTPUT_FORMAT,
                    }
                },
            ),
            "create_document_job",
        )
        _raise_for_status(response, "create_document_job")
        return response.json()

    def get_upload_urls(self, job_id: str, filename: str) -> dict:
        response = _request_with_retry(
            lambda: self._client.post(
                f"{JOB_BASE_PATH}/upload-files",
                json={"job_id": job_id, "files": [filename]},
            ),
            "get_upload_urls",
        )
        _raise_for_status(response, "get_upload_urls")
        return response.json()

    def upload_file(self, upload_url: str, file_bytes: bytes, content_type: str) -> None:
        response = _request_with_retry(
            lambda: httpx.put(
                upload_url,
                content=file_bytes,
                headers={"Content-Type": content_type, "x-ms-blob-type": "BlockBlob"},
                timeout=60.0,
            ),
            "upload_file",
        )
        if response.status_code >= 400:
            raise SarvamVisionError(
                f"Sarvam upload_file failed with status {response.status_code}: {response.text}"
            )

    def start_job(self, job_id: str) -> dict:
        response = _request_with_retry(
            lambda: self._client.post(f"{JOB_BASE_PATH}/{job_id}/start", json={}), "start_job"
        )
        _raise_for_status(response, "start_job")
        return response.json()

    def get_job_status(self, job_id: str) -> dict:
        response = _request_with_retry(
            lambda: self._client.get(f"{JOB_BASE_PATH}/{job_id}/status"), "get_job_status"
        )
        _raise_for_status(response, "get_job_status")
        return response.json()

    def wait_until_complete(self, job_id: str) -> dict:
        deadline = time.monotonic() + SARVAM_POLL_TIMEOUT_SECONDS
        while True:
            status = self.get_job_status(job_id)
            job_state = status.get("job_state")
            if job_state in ("Completed", "PartiallyCompleted"):
                return status
            if job_state == "Failed":
                raise SarvamVisionError(f"Sarvam job {job_id} failed: {status.get('error_message')}")
            if time.monotonic() >= deadline:
                raise SarvamVisionError(
                    f"Sarvam job {job_id} did not complete within {SARVAM_POLL_TIMEOUT_SECONDS}s"
                )
            time.sleep(SARVAM_POLL_INTERVAL_SECONDS)

    def get_download_urls(self, job_id: str) -> dict:
        response = _request_with_retry(
            lambda: self._client.post(f"{JOB_BASE_PATH}/{job_id}/download-files", json={}),
            "get_download_urls",
        )
        _raise_for_status(response, "get_download_urls")
        return response.json()

    def download_result(self, download_url: str) -> bytes:
        response = _request_with_retry(lambda: httpx.get(download_url, timeout=60.0), "download_result")
        if response.status_code >= 400:
            raise SarvamVisionError(
                f"Sarvam download_result failed with status {response.status_code}: {response.text}"
            )
        return response.content

    def extract_document(
        self,
        document_bytes: bytes,
        filename: str,
        content_type: str,
        language: str | None = None,
        output_format: str | None = None,
    ) -> tuple[dict[str, bytes], str, bool]:
        """Runs the full job pipeline and returns every downloaded output file
        (keyed by filename, so the parser can handle either a single ZIP or
        several individually-signed output files), the job_id for
        traceability, and whether the job only partially completed.
        """
        job = self.create_document_job(language, output_format)
        job_id = job["job_id"]

        upload_info = self.get_upload_urls(job_id, filename)
        upload_url = upload_info["upload_urls"][filename]["file_url"]
        self.upload_file(upload_url, document_bytes, content_type)

        self.start_job(job_id)
        status = self.wait_until_complete(job_id)
        partial = status.get("job_state") == "PartiallyCompleted"

        download_info = self.get_download_urls(job_id)
        download_urls = download_info.get("download_urls", {})
        if not download_urls:
            raise SarvamVisionError(f"Sarvam job {job_id} completed but returned no download_urls")

        files = {
            output_filename: self.download_result(entry["file_url"])
            for output_filename, entry in download_urls.items()
        }
        return files, job_id, partial

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SarvamVisionClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()
