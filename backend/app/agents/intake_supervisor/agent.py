import logging

from app.agents.intake_supervisor.schemas import IntakeSummary
from app.core.document_checklist import compute_missing_required_documents
from app.models.enums import LoanType

logger = logging.getLogger(__name__)

REQUIRED_FORM_FIELDS_BY_LOAN_TYPE: dict[LoanType, list[str]] = {
    LoanType.HOME: [
        "employment_type",
        "monthly_income",
        "property_value",
        "down_payment",
        "occupation_designation",
    ],
    LoanType.PERSONAL: ["employment_type", "monthly_income", "employer"],
    LoanType.BUSINESS: ["business_name", "business_type", "annual_turnover", "gst_number"],
}


def _is_blank(value) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _compute_missing_form_fields(loan_details: dict) -> list[str]:
    loan_type_raw = loan_details.get("loan_type")
    try:
        loan_type = LoanType(loan_type_raw) if loan_type_raw else None
    except ValueError:
        loan_type = None
    if loan_type is None:
        return []

    required_fields = REQUIRED_FORM_FIELDS_BY_LOAN_TYPE.get(loan_type, [])
    return [field for field in required_fields if _is_blank(loan_details.get(field))]


def _compute_sanity_warnings(loan_details: dict) -> list[str]:
    warnings: list[str] = []

    requested_amount = loan_details.get("requested_amount")
    if requested_amount is not None and requested_amount <= 0:
        warnings.append(f"Requested amount ({requested_amount}) is not positive")

    tenure = loan_details.get("tenure")
    if tenure is not None and tenure <= 0:
        warnings.append(f"Tenure ({tenure}) is not positive")

    interest_rate = loan_details.get("interest_rate")
    if interest_rate is not None and not (0 <= interest_rate <= 100):
        warnings.append(f"Interest rate ({interest_rate}) is outside a plausible 0-100 range")

    return warnings


def run(documents: list[dict], customer_profile: dict, loan_details: dict) -> IntakeSummary:
    """Deterministic intake triage: checks the loan's declared type against
    both the attached documents and the form data already on file, before
    any OCR/LLM cost is spent downstream. No LLM calls, no DB access.
    """
    missing_documents = compute_missing_required_documents(loan_details.get("loan_type"), documents)
    missing_form_fields = _compute_missing_form_fields(loan_details)
    warnings = _compute_sanity_warnings(loan_details)

    status = "failed" if missing_documents or missing_form_fields else "passed"

    return IntakeSummary(
        status=status,
        missing_documents=missing_documents,
        missing_form_fields=missing_form_fields,
        warnings=warnings,
    )
