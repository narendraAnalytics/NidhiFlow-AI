import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

DocumentValidationStatus = Literal["parsed", "failed", "skipped"]


class ExtractedDocumentFields(BaseModel):
    detected_document_type: Optional[str] = Field(
        None,
        description=(
            "Your own best guess at what kind of document this text actually is (e.g. 'PAN Card', "
            "'Aadhaar', 'Salary Slip'), independent of the declared type — used to flag a mismatch."
        ),
    )
    full_name: Optional[str] = Field(
        None, description="The document holder's full name exactly as printed on the document."
    )
    date_of_birth: Optional[str] = Field(
        None, description="Date of birth exactly as printed (preserve the original format, do not reformat)."
    )
    id_number: Optional[str] = Field(
        None,
        description=(
            "The PAN number for a PAN Card, the Aadhaar number for an Aadhaar card, or the relevant "
            "identifying number for other document types."
        ),
    )
    address: Optional[str] = Field(None, description="Postal address exactly as printed, if present.")
    employer: Optional[str] = Field(None, description="Employer/company name, if this document states one.")
    monthly_income: Optional[float] = Field(
        None,
        description=(
            "Monthly income as an explicit number stated in the document (e.g. on a salary slip). "
            "Never calculate or derive this from other figures — only use a value that is explicitly stated."
        ),
    )
    confidence: Optional[float] = Field(
        None,
        description=(
            "Your own confidence (0.0-1.0) that the fields above were extracted correctly from legible, "
            "unambiguous text. Lower it for blurry scans, cut-off text, or any field you were unsure about."
        ),
    )
    notes: Optional[str] = Field(
        None,
        description=(
            "Anything ambiguous, partially legible, or inconsistent that a human reviewer should know about "
            "this extraction (e.g. 'DOB partially obscured', 'name field appears truncated')."
        ),
    )

    @field_validator("monthly_income", mode="before")
    @classmethod
    def _coerce_currency_string(cls, value: object) -> object:
        """The extraction prompt tells the model to preserve numbers exactly as
        printed (e.g. "Rs. 1,02,334"), which directly conflicts with this field's
        float type — strip currency symbols/commas/whitespace before Pydantic's
        own float coercion runs, rather than letting one formatted string blow up
        the entire document's extraction.
        """
        if not isinstance(value, str):
            return value
        cleaned = re.sub(r"[^\d.]", "", value)
        return cleaned or None


TypeMatchStatus = Literal["match", "mismatch", "uncertain"]


class DocumentValidationResult(BaseModel):
    document_id: str
    document_type: Optional[str] = None
    status: DocumentValidationStatus
    extracted_fields: Optional[ExtractedDocumentFields] = None
    detected_document_type: Optional[str] = None
    type_match_status: Optional[TypeMatchStatus] = None
    error: Optional[str] = None


class LoanValidationSummary(BaseModel):
    validation_status: Literal["passed", "warning", "failed"]
    confidence: float
    missing_documents: list[str]
    field_mismatches: list[str]
    warnings: list[str]
