from typing import Literal, Optional

from pydantic import BaseModel

DocumentValidationStatus = Literal["parsed", "failed", "skipped"]


class ExtractedDocumentFields(BaseModel):
    detected_document_type: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    id_number: Optional[str] = None
    address: Optional[str] = None
    employer: Optional[str] = None
    monthly_income: Optional[float] = None
    notes: Optional[str] = None


class DocumentValidationResult(BaseModel):
    document_id: str
    document_type: Optional[str] = None
    status: DocumentValidationStatus
    extracted_fields: Optional[ExtractedDocumentFields] = None
    error: Optional[str] = None


class LoanValidationSummary(BaseModel):
    validation_status: Literal["passed", "warning", "failed"]
    confidence: float
    missing_documents: list[str]
    field_mismatches: list[str]
    warnings: list[str]
