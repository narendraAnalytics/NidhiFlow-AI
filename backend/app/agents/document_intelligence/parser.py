import io
import json
import zipfile

from app.agents.document_intelligence.schemas import DocumentOcrResult


class DocumentParseError(Exception):
    pass


def _parse_zip(zip_bytes: bytes) -> tuple[str | None, dict]:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        names = archive.namelist()
        markdown_name = next((n for n in names if n.endswith(".md") or n.endswith(".html")), None)
        markdown = archive.read(markdown_name).decode("utf-8") if markdown_name else None

        page_names = sorted(
            n for n in names if n.startswith("metadata/page_") and n.endswith(".json")
        )
        pages = [json.loads(archive.read(name)) for name in page_names]
        return markdown, {"pages": pages} if pages else {}


def _parse_individual_files(files: dict[str, bytes]) -> tuple[str | None, dict]:
    markdown = None
    json_payloads: dict[str, dict] = {}
    for filename, content in files.items():
        if filename.endswith(".md") or filename.endswith(".html"):
            markdown = content.decode("utf-8")
        elif filename.endswith(".json"):
            try:
                json_payloads[filename] = json.loads(content)
            except json.JSONDecodeError as exc:
                raise DocumentParseError(f"Invalid JSON in Sarvam output file '{filename}': {exc}") from exc
    return markdown, json_payloads


def _quality_warning(markdown: str | None, ocr_json: dict, page_count: int | None) -> str | None:
    """Cheap deterministic heuristic — no LLM — to flag likely-garbled or
    near-empty OCR output for human attention, rather than silently treating
    a low-yield extraction the same as a clean one.
    """
    if markdown is None:
        if ocr_json:
            return "No markdown/text was extracted — only structured page metadata was returned."
        return None

    stripped_len = len(markdown.strip())
    if page_count:
        min_expected_chars = 20 * page_count
        if stripped_len < min_expected_chars:
            return (
                f"OCR output is unusually short ({stripped_len} characters for {page_count} page(s)) — "
                "the scan may be low quality, blank, or misread."
            )
    elif stripped_len < 20:
        return "OCR output is unusually short — the scan may be low quality or blank."
    return None


def parse_ocr_output(
    files: dict[str, bytes],
    document: dict,
    job_id: str | None = None,
    partial: bool = False,
) -> DocumentOcrResult:
    """`files` is {output_filename: raw_bytes} as returned by
    SarvamVisionClient.extract_document(). Sarvam's download response may be
    a single ZIP (older/bundled shape) or several individually-signed output
    files — handle both. `ocr_json` is always normalized to `{"pages": [...]}`
    regardless of which shape Sarvam returned, so downstream consumers don't
    need to know which path produced it.
    """
    if not files:
        raise DocumentParseError("No output files returned from Sarvam")

    markdown = None
    ocr_json: dict = {}

    for content in files.values():
        if zipfile.is_zipfile(io.BytesIO(content)):
            markdown, ocr_json = _parse_zip(content)
            break
    else:
        markdown, raw_json_payloads = _parse_individual_files(files)
        pages = list(raw_json_payloads.values())
        ocr_json = {"pages": pages} if pages else {}

    if markdown is None and not ocr_json:
        raise DocumentParseError("Sarvam output contained neither markdown/html nor JSON metadata")

    page_count = len(ocr_json.get("pages", [])) if ocr_json.get("pages") else (1 if markdown else None)

    return DocumentOcrResult(
        document_id=document["id"],
        document_type=document.get("document_type"),
        status="partial" if partial else "parsed",
        ocr_markdown=markdown,
        ocr_json=ocr_json or None,
        page_count=page_count,
        job_id=job_id,
        quality_warning=_quality_warning(markdown, ocr_json, page_count),
    )
