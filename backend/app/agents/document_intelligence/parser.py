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


def parse_ocr_output(files: dict[str, bytes], document: dict) -> DocumentOcrResult:
    """`files` is {output_filename: raw_bytes} as returned by
    SarvamVisionClient.extract_document(). Sarvam's download response may be
    a single ZIP (older/bundled shape) or several individually-signed output
    files — handle both.
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
        markdown, ocr_json = _parse_individual_files(files)

    if markdown is None and not ocr_json:
        raise DocumentParseError("Sarvam output contained neither markdown/html nor JSON metadata")

    page_count = len(ocr_json.get("pages", [])) if ocr_json.get("pages") else (1 if markdown else None)

    return DocumentOcrResult(
        document_id=document["id"],
        document_type=document.get("document_type"),
        status="parsed",
        ocr_markdown=markdown,
        ocr_json=ocr_json or None,
        page_count=page_count,
    )
