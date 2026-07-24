import logging

import httpx

from app.agents.validation_compliance.prompts import build_extraction_prompt
from app.agents.validation_compliance.schemas import ExtractedDocumentFields
from app.core.config import SARVAM_API_KEY, SARVAM_BASE_URL, SARVAM_CHAT_MODEL
from app.utils.http_retry import request_with_retry

logger = logging.getLogger(__name__)

CHAT_COMPLETIONS_PATH = "/v1/chat/completions"
MAX_ATTEMPTS = 3


class SarvamValidationError(Exception):
    pass


class SarvamChatClient:
    def __init__(self) -> None:
        self._client = httpx.Client(
            base_url=SARVAM_BASE_URL,
            headers={"Authorization": f"Bearer {SARVAM_API_KEY}"},
            timeout=30.0,
        )

    def extract_fields(self, document_type: str, markdown: str) -> ExtractedDocumentFields:
        prompt = build_extraction_prompt(document_type, markdown)

        response = request_with_retry(
            lambda: self._client.post(
                CHAT_COMPLETIONS_PATH,
                json={
                    "model": SARVAM_CHAT_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    # Plain json_object mode, not strict json_schema: strict mode was
                    # observed to reliably null out `detected_document_type` (the type-
                    # mismatch signal) even when the model clearly reasoned about it in
                    # `notes` — json_object mode gets the same fields filled correctly.
                    "response_format": {"type": "json_object"},
                    # Sarvam's default max_tokens (2048) plus "thinking mode" being on by
                    # default means reasoning_content silently eats into that same budget
                    # before the model writes the JSON body — on longer documents (Sale
                    # Agreement, Bank Statement) this truncated the JSON mid-string. This
                    # is a deterministic field-extraction call, not a reasoning task, so
                    # disable thinking entirely and raise the cap for headroom.
                    "reasoning_effort": None,
                    "max_tokens": 4096,
                },
            ),
            "chat completion",
            SarvamValidationError,
            max_attempts=MAX_ATTEMPTS,
        )

        if response.status_code >= 400:
            raise SarvamValidationError(
                f"Sarvam chat completion failed with status {response.status_code}: {response.text}"
            )

        content = response.json()["choices"][0]["message"]["content"]
        if not content:
            raise SarvamValidationError("Sarvam chat completion returned an empty response")
        try:
            return ExtractedDocumentFields.model_validate_json(content)
        except Exception as exc:
            raise SarvamValidationError(f"Sarvam response did not match expected schema: {exc}") from exc

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SarvamChatClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()
