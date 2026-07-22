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

JOB_BASE_PATH = "/doc-digitization/job/v1"


class SarvamVisionError(Exception):
    pass


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
        response = self._client.post(
            f"{JOB_BASE_PATH}",
            json={
                "job_parameters": {
                    "language": language or SARVAM_VISION_LANGUAGE,
                    "output_format": output_format or SARVAM_VISION_OUTPUT_FORMAT,
                }
            },
        )
        _raise_for_status(response, "create_document_job")
        return response.json()

    def get_upload_urls(self, job_id: str, filename: str) -> dict:
        response = self._client.post(
            f"{JOB_BASE_PATH}/upload-files",
            json={"job_id": job_id, "files": [filename]},
        )
        _raise_for_status(response, "get_upload_urls")
        return response.json()

    def upload_file(self, upload_url: str, file_bytes: bytes, content_type: str) -> None:
        response = httpx.put(
            upload_url,
            content=file_bytes,
            headers={"Content-Type": content_type, "x-ms-blob-type": "BlockBlob"},
            timeout=60.0,
        )
        if response.status_code >= 400:
            raise SarvamVisionError(
                f"Sarvam upload_file failed with status {response.status_code}: {response.text}"
            )

    def start_job(self, job_id: str) -> dict:
        response = self._client.post(f"{JOB_BASE_PATH}/{job_id}/start", json={})
        _raise_for_status(response, "start_job")
        return response.json()

    def get_job_status(self, job_id: str) -> dict:
        response = self._client.get(f"{JOB_BASE_PATH}/{job_id}/status")
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
        response = self._client.post(f"{JOB_BASE_PATH}/{job_id}/download-files", json={})
        _raise_for_status(response, "get_download_urls")
        return response.json()

    def download_result(self, download_url: str) -> bytes:
        response = httpx.get(download_url, timeout=60.0)
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
    ) -> dict[str, bytes]:
        """Runs the full job pipeline and returns every downloaded output file,
        keyed by filename, so the parser can handle either a single ZIP or
        several individually-signed output files.
        """
        job = self.create_document_job(language, output_format)
        job_id = job["job_id"]

        upload_info = self.get_upload_urls(job_id, filename)
        upload_url = upload_info["upload_urls"][filename]["file_url"]
        self.upload_file(upload_url, document_bytes, content_type)

        self.start_job(job_id)
        self.wait_until_complete(job_id)

        download_info = self.get_download_urls(job_id)
        download_urls = download_info.get("download_urls", {})
        if not download_urls:
            raise SarvamVisionError(f"Sarvam job {job_id} completed but returned no download_urls")

        return {
            output_filename: self.download_result(entry["file_url"])
            for output_filename, entry in download_urls.items()
        }

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SarvamVisionClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()
