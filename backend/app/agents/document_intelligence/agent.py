import logging
import mimetypes
from concurrent.futures import ThreadPoolExecutor

from app.agents.document_intelligence.parser import DocumentParseError, parse_ocr_output
from app.agents.document_intelligence.sarvam_client import SarvamVisionClient, SarvamVisionError
from app.agents.document_intelligence.schemas import DocumentOcrResult
from app.core.config import SARVAM_API_KEY
from app.services.storage_service import StorageFetchError, get_file_bytes

logger = logging.getLogger(__name__)

SUPPORTED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}
MAX_CONCURRENT_OCR_JOBS = 4


def _guess_mime_type(filename: str) -> str:
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


def _extract_one(client: SarvamVisionClient, document: dict) -> DocumentOcrResult:
    document_id = document.get("id")
    document_type = document.get("document_type")

    if not SARVAM_API_KEY:
        return DocumentOcrResult(
            document_id=document_id,
            document_type=document_type,
            status="skipped",
            error="SARVAM_API_KEY not configured",
        )

    firebase_url = document.get("firebase_url")
    if not firebase_url:
        return DocumentOcrResult(
            document_id=document_id,
            document_type=document_type,
            status="failed",
            error="Document has no firebase_url",
        )

    filename = document.get("document_name") or f"{document_id}"
    mime_type = _guess_mime_type(filename)
    if mime_type not in SUPPORTED_MIME_TYPES:
        return DocumentOcrResult(
            document_id=document_id,
            document_type=document_type,
            status="failed",
            error=f"Unsupported mime type '{mime_type}' for Sarvam Vision",
        )

    try:
        file_bytes = get_file_bytes(firebase_url)
    except StorageFetchError as exc:
        logger.exception("storage fetch failed for document_id=%s", document_id)
        return DocumentOcrResult(
            document_id=document_id, document_type=document_type, status="failed", error=str(exc)
        )

    try:
        files, job_id, partial = client.extract_document(file_bytes, filename, mime_type)
        return parse_ocr_output(files, document, job_id=job_id, partial=partial)
    except (SarvamVisionError, DocumentParseError) as exc:
        logger.exception("Sarvam OCR failed for document_id=%s", document_id)
        return DocumentOcrResult(
            document_id=document_id, document_type=document_type, status="failed", error=str(exc)
        )
    except Exception as exc:
        # Isolate failures per document — one bad file/response must not abort
        # the whole batch (that would force a full node-level retry that
        # re-OCRs every other document too).
        logger.exception("Unexpected error extracting document_id=%s", document_id)
        return DocumentOcrResult(
            document_id=document_id,
            document_type=document_type,
            status="failed",
            error=f"Unexpected error during OCR: {exc}",
        )


def run(documents: list[dict]) -> list[DocumentOcrResult]:
    if not documents:
        return []

    if not SARVAM_API_KEY:
        return [
            DocumentOcrResult(
                document_id=doc.get("id"),
                document_type=doc.get("document_type"),
                status="skipped",
                error="SARVAM_API_KEY not configured",
            )
            for doc in documents
        ]

    with SarvamVisionClient() as client:
        # httpx.Client is safe for concurrent requests across threads, so
        # documents are OCR'd in parallel instead of one full
        # create->upload->poll->download cycle at a time — this is the
        # dominant latency cost for multi-document loan applications.
        with ThreadPoolExecutor(max_workers=min(MAX_CONCURRENT_OCR_JOBS, len(documents))) as executor:
            return list(executor.map(lambda document: _extract_one(client, document), documents))
