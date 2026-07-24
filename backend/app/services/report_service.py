import io
import uuid
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from decimal import Decimal

from app.agents.validation_compliance.agent import (
    INCOME_BEARING_DOCUMENT_TYPES,
    _compute_emi,
    _normalize,
    _normalize_id,
)
from app.models.customer import Customer
from app.models.document_validation_result import DocumentValidationResult
from app.models.loan_application import LoanApplication
from app.models.loan_document import LoanDocument
from app.models.loan_validation_summary import LoanValidationSummary
from app.models.workflow_event import WorkflowEvent
from app.models.workflow_execution import WorkflowExecution
from app.services.reporting_service import LoanNotFoundError
from app.utils.friendly_messages import friendly_decision_message

BRAND_COLOR = colors.HexColor("#3B82F6")
MUTED_COLOR = colors.HexColor("#5b6b8c")
HEADING_COLOR = colors.HexColor("#0f1b33")
GRID_COLOR = colors.HexColor("#e2e8f5")
ROW_TINT = colors.HexColor("#f8fbff")
PASS_COLOR = "#15803d"
NA_COLOR = "#9aa8c2"
REVIEW_COLOR = "#b45309"

# Display-friendly wording for internal processing statuses — the underlying
# processing_status/type_match_status values in the DB are left untouched;
# only how they're rendered in the human-facing PDF changes here.
PROCESSING_STATUS_LABELS = {
    "parsed": "Verified",
    "partial": "Partially Verified",
    "failed": "Needs Manual Review",
    "skipped": "Not Processed",
    "pending": "Pending",
}
TYPE_CHECK_LABELS = {
    "match": "Match",
    "mismatch": "Needs Review",
    "uncertain": "Uncertain",
}


def _processing_status_label(raw_status: str) -> str:
    return PROCESSING_STATUS_LABELS.get(raw_status, raw_status.title())


def _type_check_label(raw_status: str) -> str:
    if raw_status == "—":
        return raw_status
    return TYPE_CHECK_LABELS.get(raw_status, raw_status.title())


LOAN_DETAIL_FIELDS: list[tuple[str, str]] = [
    ("loan_purpose", "Purpose"),
    ("tenure", "Tenure (months)"),
    ("interest_rate", "Interest Rate (%)"),
    ("employment_type", "Employment Type"),
    ("employer", "Employer"),
    ("monthly_income", "Monthly Income"),
    ("credit_score", "Credit Score"),
    ("existing_emi", "Existing EMI"),
    ("branch", "Branch"),
    ("occupation_designation", "Occupation / Designation"),
    ("total_work_experience", "Total Work Experience"),
    ("experience_current_employer", "Experience with Current Employer"),
    ("property_type", "Property Type"),
    ("property_status", "Property Status"),
    ("builder_developer_name", "Builder / Developer"),
    ("property_value", "Property Value"),
    ("down_payment", "Down Payment"),
    ("employment_experience_years", "Employment Experience (years)"),
    ("existing_loan_outstanding", "Existing Loan Outstanding"),
    ("bank_name", "Salary Account Bank"),
    ("monthly_household_expenses", "Monthly Household Expenses"),
    ("business_name", "Business Name"),
    ("business_type", "Business Type"),
    ("industry", "Industry"),
    ("business_vintage_years", "Business Vintage (years)"),
    ("annual_turnover", "Annual Turnover"),
    ("monthly_business_revenue", "Monthly Business Revenue"),
    ("monthly_net_profit", "Monthly Net Profit"),
    ("gst_number", "GST Number"),
    ("udyam_registration_number", "Udyam Registration Number"),
    ("cin_llpin", "CIN / LLPIN"),
    ("number_of_employees", "Number of Employees"),
    ("existing_business_loan_outstanding", "Existing Business Loan Outstanding"),
    ("business_bank_name", "Business Bank Name"),
    ("collateral_required", "Collateral Required"),
    ("collateral_type", "Collateral Type"),
    ("collateral_value", "Collateral Value"),
]


_BASE_STYLES = getSampleStyleSheet()
CELL_LABEL_STYLE = ParagraphStyle(
    "CellLabel", parent=_BASE_STYLES["Normal"], textColor=MUTED_COLOR, fontSize=9.5, fontName="Helvetica-Bold", leading=12
)
CELL_VALUE_STYLE = ParagraphStyle(
    "CellValue", parent=_BASE_STYLES["Normal"], textColor=HEADING_COLOR, fontSize=9.5, leading=12
)
TABLE_HEADER_STYLE = ParagraphStyle(
    "TableHeader", parent=_BASE_STYLES["Normal"], textColor=colors.white, fontSize=9, fontName="Helvetica-Bold", leading=11
)
TABLE_CELL_STYLE = ParagraphStyle("TableCell", parent=_BASE_STYLES["Normal"], textColor=HEADING_COLOR, fontSize=9, leading=11)


def _kv_table(rows: list[tuple[str, str]], col_widths=(50 * mm, 115 * mm)) -> Table:
    wrapped_rows = [
        [Paragraph(str(label), CELL_LABEL_STYLE), Paragraph(str(value), CELL_VALUE_STYLE)] for label, value in rows
    ]
    table = Table(wrapped_rows, colWidths=list(col_widths))
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, -1), 0.4, GRID_COLOR),
            ]
        )
    )
    return table


def _wrap_row(cells: list[str], style: ParagraphStyle) -> list:
    return [Paragraph(str(cell), style) for cell in cells]


def _extracted_fields_for_type(
    documents: list[LoanDocument],
    validation_by_document: dict[uuid.UUID, DocumentValidationResult],
    document_type_value: str,
) -> dict | None:
    for document in documents:
        if document.document_type.value != document_type_value:
            continue
        validation = validation_by_document.get(document.id)
        if validation and validation.extracted_fields:
            return validation.extracted_fields
    return None


def _build_verification_checklist(
    customer: Customer | None,
    loan: LoanApplication,
    documents: list[LoanDocument],
    validation_by_document: dict[uuid.UUID, DocumentValidationResult],
) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Returns (checklist rows, recommendations). Each checklist row is
    (label, status in {"Yes","No","N/A"}, detail). Mirrors the checks
    already performed in validation_compliance/agent.py's cross-document
    step, but recomputed here from the persisted extracted_fields so the
    report can present them as a plain itemized Yes/No list.
    """
    checklist: list[tuple[str, str, str]] = []
    recommendations: list[str] = []

    uploaded_types = {d.document_type.value for d in documents}
    has_pan = "PAN Card" in uploaded_types
    has_aadhaar = "Aadhaar" in uploaded_types
    checklist.append(("PAN Card Uploaded", "Yes" if has_pan else "No", ""))
    checklist.append(("Aadhaar Card Uploaded", "Yes" if has_aadhaar else "No", ""))

    pan_fields = _extracted_fields_for_type(documents, validation_by_document, "PAN Card")
    aadhaar_fields = _extracted_fields_for_type(documents, validation_by_document, "Aadhaar")

    if pan_fields and aadhaar_fields:
        pan_name, aadhaar_name = pan_fields.get("full_name"), aadhaar_fields.get("full_name")
        if pan_name and aadhaar_name:
            match = _normalize(pan_name) == _normalize(aadhaar_name)
            checklist.append(("PAN Name Matches Aadhaar Name", "Yes" if match else "No", ""))
            if not match:
                recommendations.append("The name on the PAN card and Aadhaar card do not match — please verify with the applicant.")
        pan_dob, aadhaar_dob = pan_fields.get("date_of_birth"), aadhaar_fields.get("date_of_birth")
        if pan_dob and aadhaar_dob:
            match = pan_dob == aadhaar_dob
            checklist.append(("PAN Date of Birth Matches Aadhaar", "Yes" if match else "No", ""))
            if not match:
                recommendations.append("The date of birth on the PAN card and Aadhaar card do not match — please verify with the applicant.")

    if customer and pan_fields and pan_fields.get("id_number"):
        match = _normalize_id(pan_fields["id_number"]) == _normalize_id(customer.pan)
        checklist.append(("PAN Number Matches Application Record", "Yes" if match else "No", ""))
        if not match:
            recommendations.append("The PAN number extracted from the uploaded document does not match the applicant's record.")

    if customer and aadhaar_fields and aadhaar_fields.get("id_number"):
        match = _normalize_id(aadhaar_fields["id_number"]) == _normalize_id(customer.aadhaar)
        checklist.append(("Aadhaar Number Matches Application Record", "Yes" if match else "No", ""))
        if not match:
            recommendations.append("The Aadhaar number extracted from the uploaded document does not match the applicant's record.")

    if customer:
        candidate_names = [f.get("full_name") for f in (pan_fields, aadhaar_fields) if f and f.get("full_name")]
        if candidate_names:
            match = any(_normalize(name) == _normalize(customer.full_name) for name in candidate_names)
            checklist.append(("Applicant Name Matches Uploaded Documents", "Yes" if match else "No", ""))
            if not match:
                recommendations.append("The applicant's name on file does not match the name on the identity documents.")

    income_value = None
    income_verified = False
    for doc_type in INCOME_BEARING_DOCUMENT_TYPES:
        fields = _extracted_fields_for_type(documents, validation_by_document, doc_type)
        if fields and fields.get("monthly_income"):
            income_value = Decimal(str(fields["monthly_income"]))
            income_verified = True
            break
    checklist.append(("Income Verified From Documents", "Yes" if income_verified else "No", ""))
    if not income_verified:
        recommendations.append(
            "Monthly income could not be confirmed from the uploaded documents (e.g. Salary Slip, Form 16, ITR) — "
            "the EMI check below uses the self-reported income instead."
        )

    if income_value is None and loan.monthly_income is not None:
        income_value = Decimal(str(loan.monthly_income))

    if income_value is not None and loan.requested_amount and loan.interest_rate and loan.tenure:
        try:
            emi = _compute_emi(Decimal(str(loan.requested_amount)), Decimal(str(loan.interest_rate)), int(loan.tenure))
            affordable = income_value >= emi
            income_label = "verified" if income_verified else "self-reported"
            checklist.append(
                (
                    f"Estimated EMI Within Income ({income_label})",
                    "Yes" if affordable else "No",
                    f"EMI ~Rs. {emi:,.0f} vs income Rs. {income_value:,.0f}",
                )
            )
            if not affordable:
                recommendations.append(
                    "The estimated EMI exceeds the applicant's monthly income — consider a longer tenure, "
                    "a co-applicant, or a lower loan amount."
                )
        except (ValueError, ArithmeticError):
            pass

    for document in documents:
        validation = validation_by_document.get(document.id)
        if not validation or not validation.type_match_status:
            continue
        status = {"match": "Yes", "mismatch": "No", "uncertain": "N/A"}.get(validation.type_match_status, "N/A")
        checklist.append((f"Document Type Verified: {document.document_type.value}", status, document.document_name))
        if status == "No":
            recommendations.append(
                f"'{document.document_name}' was declared as {document.document_type.value} but appears to be a "
                f"different document — please confirm or re-upload."
            )

    return checklist, recommendations


def _build_ai_operations_summary(
    customer: Customer | None,
    loan: LoanApplication,
    checklist: list[tuple[str, str, str]],
    summary: LoanValidationSummary | None,
) -> dict:
    """Builds a short, friendly narrative summary of the automated checks —
    presentation only, derived entirely from data already computed by
    `_build_verification_checklist` and the persisted `LoanValidationSummary`.
    No new LLM call and no new data source; this never overrides the actual
    routing decision, only how it's explained back to the applicant.
    """
    greeting = f"Dear {customer.full_name}," if customer and customer.full_name else "Dear Applicant,"
    intro = (
        f"We have completed scanning and reviewing the documents you submitted for your "
        f"{loan.loan_type.value} Loan application."
    )

    status_by_label = {label: status for label, status, _ in checklist}

    nice_points: list[str] = []
    credit_score = loan.credit_score
    if credit_score is not None:
        if credit_score >= 750:
            nice_points.append(f"Your credit score of {credit_score} is excellent.")
        elif credit_score >= 700:
            nice_points.append(f"Your credit score of {credit_score} is good.")

    for label, status in status_by_label.items():
        if label.startswith("Estimated EMI Within Income") and status == "Yes":
            nice_points.append("Your estimated monthly EMI comfortably fits within your income.")
            break

    if status_by_label.get("Income Verified From Documents") == "Yes":
        nice_points.append("Your income was independently confirmed from your uploaded documents.")

    identity_labels = [
        "PAN Name Matches Aadhaar Name",
        "PAN Date of Birth Matches Aadhaar",
        "PAN Number Matches Application Record",
        "Aadhaar Number Matches Application Record",
        "Applicant Name Matches Uploaded Documents",
    ]
    identity_results = [status_by_label[label] for label in identity_labels if label in status_by_label]
    if identity_results and all(result == "Yes" for result in identity_results):
        nice_points.append("Your identity documents were verified successfully and all details matched.")

    doc_type_results = [status for label, status in status_by_label.items() if label.startswith("Document Type Verified")]
    if doc_type_results and all(result == "Yes" for result in doc_type_results):
        nice_points.append("All your uploaded documents were correctly verified against their declared type.")

    if not nice_points:
        nice_points.append("Your documents have been received and are being processed.")

    if loan.status.value == "Human Review":
        routing_message = (
            "Your application will now be sent to our Branch Manager for a final human review, "
            "as required by our lending policy."
        )
    elif loan.status.value in ("Processing", "Approved", "Completed"):
        routing_message = "Your application passed automated checks and is proceeding in the pipeline."
    elif loan.status.value == "Rejected":
        routing_message = "This application was not approved."
    else:
        routing_message = "This application has not yet been submitted for processing."

    yes_count = sum(1 for status in status_by_label.values() if status == "Yes")
    no_count = sum(1 for status in status_by_label.values() if status == "No")
    base_ratio = (yes_count / (yes_count + no_count)) if (yes_count + no_count) else 0.5
    missing_count = len(summary.missing_documents) if summary and summary.missing_documents else 0
    likelihood = max(0.05, min(0.95, base_ratio - 0.15 * missing_count))
    likelihood_pct = round(likelihood * 100)

    return {
        "greeting": greeting,
        "intro": intro,
        "nice_points": nice_points,
        "routing_message": routing_message,
        "likelihood_pct": likelihood_pct,
    }


def build_loan_report_pdf(db: Session, loan_id: uuid.UUID) -> bytes:
    loan = db.query(LoanApplication).filter(LoanApplication.id == loan_id).first()
    if loan is None:
        raise LoanNotFoundError(f"Loan application {loan_id} not found")

    customer = db.query(Customer).filter(Customer.id == loan.customer_id).first()
    documents = (
        db.query(LoanDocument)
        .filter(LoanDocument.loan_application_id == loan_id)
        .order_by(LoanDocument.upload_time)
        .all()
    )
    validation_by_document: dict[uuid.UUID, DocumentValidationResult] = {}
    if documents:
        results = (
            db.query(DocumentValidationResult)
            .filter(DocumentValidationResult.document_id.in_([d.id for d in documents]))
            .order_by(DocumentValidationResult.created_at)
            .all()
        )
        for result in results:
            validation_by_document[result.document_id] = result  # last write wins -> latest

    summary = (
        db.query(LoanValidationSummary)
        .filter(LoanValidationSummary.loan_application_id == loan_id)
        .order_by(LoanValidationSummary.created_at.desc())
        .first()
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("ReportTitle", parent=styles["Title"], textColor=HEADING_COLOR, fontSize=19, spaceAfter=2)
    subtitle_style = ParagraphStyle("ReportSubtitle", parent=styles["Normal"], textColor=MUTED_COLOR, fontSize=9.5)
    section_style = ParagraphStyle("SectionHeading", parent=styles["Heading2"], textColor=HEADING_COLOR, fontSize=13, spaceBefore=16, spaceAfter=6)
    sub_section_style = ParagraphStyle(
        "SubSectionHeading",
        parent=styles["Heading3"],
        textColor=HEADING_COLOR,
        fontName="Helvetica-Bold",
        fontSize=10.5,
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle("Body", parent=styles["Normal"], textColor=HEADING_COLOR, fontSize=10)
    muted_style = ParagraphStyle("Muted", parent=styles["Normal"], textColor=MUTED_COLOR, fontSize=9)
    bullet_style = ParagraphStyle("Bullet", parent=styles["Normal"], textColor=HEADING_COLOR, fontSize=9.5, leftIndent=10, spaceAfter=2)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        title=f"NidhiFlow AI - Loan Application Summary {loan_id}",
    )

    story = [
        Paragraph("NidhiFlow AI", ParagraphStyle("Brand", parent=styles["Normal"], textColor=BRAND_COLOR, fontSize=11, spaceAfter=4)),
        Paragraph("Loan Application Summary", title_style),
        Paragraph(
            f"Generated {datetime.now(timezone.utc).strftime('%d %b %Y, %H:%M UTC')}",
            subtitle_style,
        ),
        Spacer(1, 6 * mm),
    ]

    # --- Applicant Details ---
    story.append(Paragraph("Applicant Details", section_style))
    if customer:
        applicant_rows = [
            ["Full Name", customer.full_name],
            ["PAN", customer.pan],
            ["Aadhaar", customer.aadhaar],
            ["Phone", customer.phone],
            ["Email", customer.email],
        ]
        if customer.address:
            applicant_rows.append(["Address", customer.address])
        if customer.age is not None:
            applicant_rows.append(["Age", str(customer.age)])
        if customer.city:
            applicant_rows.append(["City", customer.city])
        story.append(_kv_table(applicant_rows))
    else:
        story.append(Paragraph("Applicant record not found.", body_style))

    # --- Loan Details ---
    story.append(Paragraph("Loan Details", section_style))
    loan_rows = [
        ["Loan Type", loan.loan_type.value],
        ["Requested Amount", f"Rs. {loan.requested_amount:,.2f}"],
        ["Status", loan.status.value],
        ["Applied On", loan.created_at.strftime("%d %b %Y")],
    ]
    for attr, label in LOAN_DETAIL_FIELDS:
        value = getattr(loan, attr, None)
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            value = "Yes" if value else "No"
        elif hasattr(value, "quantize"):
            value = f"{value:,.2f}"
        loan_rows.append([label, str(value)])
    story.append(_kv_table(loan_rows))

    # --- Documents Submitted & Examined ---
    story.append(Paragraph("Documents Submitted & Examined", section_style))
    if documents:
        doc_rows = [_wrap_row(["Document Type", "File Name", "Processing Status", "Type Check"], TABLE_HEADER_STYLE)]
        for document in documents:
            validation = validation_by_document.get(document.id)
            processing_status = _processing_status_label(validation.processing_status if validation else "pending")
            type_check = _type_check_label(validation.type_match_status if validation and validation.type_match_status else "—")
            doc_rows.append(
                _wrap_row(
                    [document.document_type.value, document.document_name, processing_status, type_check],
                    TABLE_CELL_STYLE,
                )
            )
        doc_table = Table(doc_rows, colWidths=[38 * mm, 62 * mm, 25 * mm, 25 * mm])
        doc_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), HEADING_COLOR),
                    ("GRID", (0, 0), (-1, -1), 0.5, GRID_COLOR),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_TINT]),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(doc_table)
    else:
        story.append(Paragraph("No documents were uploaded for this application.", body_style))

    # --- Verification Checklist ---
    story.append(Paragraph("Verification Checklist", section_style))
    if summary:
        story.append(
            Paragraph(
                f"Overall confidence: <b>{summary.confidence * 100:.0f}%</b>",
                body_style,
            )
        )
    checklist, recommendations = _build_verification_checklist(customer, loan, documents, validation_by_document)
    if summary and not summary.missing_documents:
        checklist.insert(0, ("Required Documents Complete", "Yes", ""))
    if checklist:
        checklist_rows = [_wrap_row(["Check", "Result", "Detail"], TABLE_HEADER_STYLE)]
        for label, status, detail in checklist:
            color = {"Yes": PASS_COLOR, "No": REVIEW_COLOR, "Review": REVIEW_COLOR}.get(status, NA_COLOR)
            checklist_rows.append(
                [
                    Paragraph(label, TABLE_CELL_STYLE),
                    Paragraph(f"<font color='{color}'><b>{status}</b></font>", TABLE_CELL_STYLE),
                    Paragraph(detail, TABLE_CELL_STYLE),
                ]
            )
        checklist_table = Table(checklist_rows, colWidths=[70 * mm, 22 * mm, 73 * mm])
        checklist_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), HEADING_COLOR),
                    ("GRID", (0, 0), (-1, -1), 0.5, GRID_COLOR),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_TINT]),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(checklist_table)
    else:
        story.append(Paragraph("Not enough data was extracted yet to run verification checks.", body_style))

    if recommendations:
        story.append(Paragraph("Recommendations", sub_section_style))
        for recommendation in recommendations:
            story.append(Paragraph(f"&bull; {recommendation}", bullet_style))

    # --- AI Operations Summary ---
    story.append(Paragraph("AI Operations Summary", section_style))
    ai_summary = _build_ai_operations_summary(customer, loan, checklist, summary)
    story.append(Paragraph(ai_summary["greeting"], body_style))
    story.append(Paragraph(ai_summary["intro"], body_style))
    for point in ai_summary["nice_points"]:
        story.append(Paragraph(f"&bull; {point}", bullet_style))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(ai_summary["routing_message"], body_style))
    story.append(
        Paragraph(
            f"Indicative application strength: <b>{ai_summary['likelihood_pct']}%</b> — this is an automated "
            "estimate based on document and eligibility checks only. It is not a loan sanction, offer, or "
            "guarantee of approval; the final decision rests solely with the Branch Manager / human underwriter.",
            muted_style,
        )
    )

    # --- Final Result ---
    story.append(Paragraph("Final Result", section_style))
    story.append(Paragraph(f"<b>{loan.status.value}</b> — {ai_summary['routing_message']}", body_style))

    latest_execution = (
        db.query(WorkflowExecution)
        .filter(WorkflowExecution.loan_application_id == loan_id)
        .order_by(WorkflowExecution.started_at.desc())
        .first()
    )
    decision_event = None
    if latest_execution:
        decision_event = (
            db.query(WorkflowEvent)
            .filter(
                WorkflowEvent.workflow_execution_id == latest_execution.id,
                WorkflowEvent.event_type == "Pipeline Decision",
            )
            .order_by(WorkflowEvent.created_at.desc())
            .first()
        )
    if decision_event and decision_event.message:
        story.append(Paragraph(friendly_decision_message(decision_event.message), muted_style))

    story.append(Spacer(1, 8 * mm))
    story.append(
        Paragraph(
            "NidhiFlow AI is designed using principles from the RBI Digital Lending Directions, 2025. "
            "AI assists with document intake, validation and pipeline operations only — the lending "
            "decision is made by a human underwriter. This report is generated automatically.",
            muted_style,
        )
    )

    doc.build(story)
    return buffer.getvalue()
