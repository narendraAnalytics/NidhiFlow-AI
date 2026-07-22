import logging

from google import genai
from google.genai import errors, types

from app.agents.validation_compliance.prompts import build_extraction_prompt
from app.agents.validation_compliance.schemas import ExtractedDocumentFields
from app.core.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_TIMEOUT_SECONDS,
    GEMINI_USE_VERTEX,
    GEMINI_VERTEX_LOCATION,
    GEMINI_VERTEX_PROJECT,
)

logger = logging.getLogger(__name__)


class GeminiValidationError(Exception):
    pass


def _build_client() -> genai.Client:
    http_options = types.HttpOptions(timeout=int(GEMINI_TIMEOUT_SECONDS * 1000))
    if GEMINI_USE_VERTEX:
        return genai.Client(
            vertexai=True,
            project=GEMINI_VERTEX_PROJECT,
            location=GEMINI_VERTEX_LOCATION,
            http_options=http_options,
        )
    return genai.Client(api_key=GEMINI_API_KEY, http_options=http_options)


class GeminiClient:
    def __init__(self) -> None:
        self._client = _build_client()

    def extract_fields(self, document_type: str, markdown: str) -> ExtractedDocumentFields:
        prompt = build_extraction_prompt(document_type, markdown)

        try:
            response = self._client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractedDocumentFields,
                    temperature=0,
                ),
            )
        except errors.ClientError as exc:
            logger.warning(
                "Gemini rejected response_schema config (model=%s), falling back to "
                "unstructured JSON parsing: %s",
                GEMINI_MODEL,
                exc,
            )
            return self._extract_fields_fallback(prompt)
        except errors.ServerError as exc:
            raise GeminiValidationError(f"Gemini server error: {exc}") from exc

        if response.parsed is not None:
            return response.parsed

        # response_schema was accepted but no parsed object came back — fall
        # back to manual text parsing rather than failing outright.
        return self._parse_text(response.text)

    def _extract_fields_fallback(self, prompt: str) -> ExtractedDocumentFields:
        try:
            response = self._client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0,
                ),
            )
        except (errors.ClientError, errors.ServerError) as exc:
            raise GeminiValidationError(f"Gemini fallback call failed: {exc}") from exc

        return self._parse_text(response.text)

    def _parse_text(self, text: str | None) -> ExtractedDocumentFields:
        if not text:
            raise GeminiValidationError("Gemini returned an empty response")
        try:
            return ExtractedDocumentFields.model_validate_json(text)
        except Exception as exc:
            raise GeminiValidationError(f"Gemini response did not match expected schema: {exc}") from exc
