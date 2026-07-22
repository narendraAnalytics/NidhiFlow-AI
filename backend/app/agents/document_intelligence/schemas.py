from typing import Literal, Optional

from pydantic import BaseModel

DocumentOcrStatus = Literal["parsed", "failed", "skipped"]


class DocumentOcrResult(BaseModel):
    document_id: str
    document_type: Optional[str] = None
    status: DocumentOcrStatus
    ocr_markdown: Optional[str] = None
    ocr_json: Optional[dict] = None
    page_count: Optional[int] = None
    error: Optional[str] = None
