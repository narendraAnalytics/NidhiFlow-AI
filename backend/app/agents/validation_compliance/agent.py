import logging
from decimal import Decimal

from app.agents.validation_compliance.gemini_client import GeminiClient, GeminiValidationError
from app.agents.validation_compliance.schemas import (
    DocumentValidationResult,
    ExtractedDocumentFields,
    LoanValidationSummary,
)
from app.core.config import GEMINI_API_KEY, GEMINI_USE_VERTEX

logger = logging.getLogger(__name__)

REQUIRED_DOCUMENT_TYPES = {"PAN Card", "Aadhaar"}
INCOME_BEARING_DOCUMENT_TYPES = {"Salary Slip", "ITR", "Income Proof"}


def _normalize(value: str | None) -> str | None:
    if value is None:
        return None
    return " ".join(value.strip().lower().split())


def _extract_one(
    client: GeminiClient, document: dict, ocr_result: dict | None
) -> DocumentValidationResult:
    document_id = document.get("id")
    document_type = document.get("document_type")

    if ocr_result is None or ocr_result.get("status") != "parsed" or not ocr_result.get("ocr_markdown"):
        return DocumentValidationResult(
            document_id=document_id,
            document_type=document_type,
            status="skipped",
            error="No OCR markdown available for this document",
        )

    try:
        fields = client.extract_fields(document_type, ocr_result["ocr_markdown"])
        return DocumentValidationResult(
            document_id=document_id,
            document_type=document_type,
            status="parsed",
            extracted_fields=fields,
        )
    except GeminiValidationError as exc:
        logger.exception("Gemini extraction failed for document_id=%s", document_id)
        return DocumentValidationResult(
            document_id=document_id, document_type=document_type, status="failed", error=str(exc)
        )


def _compute_emi(principal: Decimal, annual_interest_rate: Decimal, tenure_months: int) -> Decimal:
    if tenure_months <= 0:
        raise ValueError("tenure_months must be positive")
    monthly_rate = annual_interest_rate / Decimal(12) / Decimal(100)
    if monthly_rate == 0:
        return principal / tenure_months
    factor = (1 + monthly_rate) ** tenure_months
    return principal * monthly_rate * factor / (factor - 1)


def _cross_check(
    results: list[DocumentValidationResult],
    documents: list[dict],
    customer_profile: dict,
    loan_details: dict,
) -> LoanValidationSummary:
    warnings: list[str] = []
    field_mismatches: list[str] = []
    checks_performed = 0
    mismatches = 0

    for result in results:
        if result.status == "failed":
            warnings.append(f"Extraction failed for {result.document_type or result.document_id}: {result.error}")
        elif result.status == "skipped":
            warnings.append(f"Extraction skipped for {result.document_type or result.document_id}: {result.error}")

    present_types = {doc.get("document_type") for doc in documents}
    missing_documents = sorted(t for t in REQUIRED_DOCUMENT_TYPES if t not in present_types)

    extracted_by_type: dict[str, ExtractedDocumentFields] = {
        result.document_type: result.extracted_fields
        for result in results
        if result.status == "parsed" and result.extracted_fields is not None and result.document_type
    }

    pan_fields = extracted_by_type.get("PAN Card")
    aadhaar_fields = extracted_by_type.get("Aadhaar")

    if pan_fields and aadhaar_fields:
        checks_performed += 1
        if _normalize(pan_fields.full_name) and _normalize(aadhaar_fields.full_name):
            if _normalize(pan_fields.full_name) != _normalize(aadhaar_fields.full_name):
                mismatches += 1
                field_mismatches.append(
                    f"PAN name ('{pan_fields.full_name}') does not match Aadhaar name ('{aadhaar_fields.full_name}')"
                )

        checks_performed += 1
        if pan_fields.date_of_birth and aadhaar_fields.date_of_birth:
            if pan_fields.date_of_birth != aadhaar_fields.date_of_birth:
                mismatches += 1
                field_mismatches.append(
                    f"PAN DOB ('{pan_fields.date_of_birth}') does not match Aadhaar DOB ('{aadhaar_fields.date_of_birth}')"
                )

    customer_pan = customer_profile.get("pan")
    if pan_fields and pan_fields.id_number and customer_pan:
        checks_performed += 1
        if _normalize(pan_fields.id_number) != _normalize(customer_pan):
            mismatches += 1
            field_mismatches.append(
                f"Extracted PAN number ('{pan_fields.id_number}') does not match the PAN on file"
            )

    customer_aadhaar = customer_profile.get("aadhaar")
    if aadhaar_fields and aadhaar_fields.id_number and customer_aadhaar:
        checks_performed += 1
        if _normalize(aadhaar_fields.id_number) != _normalize(customer_aadhaar):
            mismatches += 1
            field_mismatches.append(
                f"Extracted Aadhaar number ('{aadhaar_fields.id_number}') does not match the Aadhaar on file"
            )

    customer_name = customer_profile.get("full_name")
    if customer_name:
        candidate_names = [f.full_name for f in (pan_fields, aadhaar_fields) if f and f.full_name]
        if candidate_names:
            checks_performed += 1
            if not any(_normalize(name) == _normalize(customer_name) for name in candidate_names):
                mismatches += 1
                field_mismatches.append(
                    f"Extracted document name(s) {candidate_names} do not match the customer's name on file ('{customer_name}')"
                )

    # EMI affordability check: income > estimated monthly installment.
    requested_amount = loan_details.get("requested_amount")
    interest_rate = loan_details.get("interest_rate")
    tenure = loan_details.get("tenure")
    if requested_amount is None or interest_rate is None or not tenure:
        warnings.append("EMI check skipped: requested_amount/interest_rate/tenure not fully available")
    else:
        income = None
        for doc_type in INCOME_BEARING_DOCUMENT_TYPES:
            fields = extracted_by_type.get(doc_type)
            if fields and fields.monthly_income:
                income = Decimal(str(fields.monthly_income))
                break
        if income is None and loan_details.get("monthly_income") is not None:
            income = Decimal(str(loan_details["monthly_income"]))

        if income is None:
            warnings.append("EMI check skipped: no income data available from documents or application")
        else:
            try:
                emi = _compute_emi(Decimal(str(requested_amount)), Decimal(str(interest_rate)), int(tenure))
            except (ValueError, ArithmeticError) as exc:
                warnings.append(f"EMI check skipped: could not compute EMI ({exc})")
            else:
                checks_performed += 1
                if income < emi:
                    mismatches += 1
                    field_mismatches.append(
                        f"Monthly income ({income}) is less than the estimated EMI ({emi:.2f}) for the requested loan"
                    )

    if checks_performed == 0:
        confidence = 0.0
        warnings.append("Insufficient data to perform any cross-checks")
    else:
        confidence = round((checks_performed - mismatches) / checks_performed, 4)

    if missing_documents or field_mismatches:
        validation_status = "failed"
    elif warnings:
        validation_status = "warning"
    else:
        validation_status = "passed"

    return LoanValidationSummary(
        validation_status=validation_status,
        confidence=confidence,
        missing_documents=missing_documents,
        field_mismatches=field_mismatches,
        warnings=warnings,
    )


def run(
    documents: list[dict],
    ocr_results: list[dict],
    customer_profile: dict,
    loan_details: dict,
) -> tuple[list[DocumentValidationResult], LoanValidationSummary]:
    ocr_by_document_id = {r.get("document_id"): r for r in ocr_results}

    if not GEMINI_API_KEY and not GEMINI_USE_VERTEX:
        results = [
            DocumentValidationResult(
                document_id=doc.get("id"),
                document_type=doc.get("document_type"),
                status="skipped",
                error="GEMINI_API_KEY not configured",
            )
            for doc in documents
        ]
    elif not documents:
        results = []
    else:
        client = GeminiClient()
        results = [
            _extract_one(client, document, ocr_by_document_id.get(document.get("id")))
            for document in documents
        ]

    summary = _cross_check(results, documents, customer_profile, loan_details)
    return results, summary
