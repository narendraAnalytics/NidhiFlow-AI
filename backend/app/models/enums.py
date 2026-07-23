import enum


class LoanType(str, enum.Enum):
    HOME = "Home"
    PERSONAL = "Personal"
    BUSINESS = "Business"


class LoanStatus(str, enum.Enum):
    DRAFT = "Draft"
    DOCUMENTS_UPLOADED = "Documents Uploaded"
    PROCESSING = "Processing"
    HUMAN_REVIEW = "Human Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    COMPLETED = "Completed"


class DocumentCategory(str, enum.Enum):
    IDENTITY = "Identity Proof"
    INCOME = "Income Proof"
    PROPERTY = "Property Documents"
    BUSINESS = "Business Documents"
    OTHER = "Other"


class DocumentType(str, enum.Enum):
    PAN_CARD = "PAN Card"
    AADHAAR = "Aadhaar"
    SALARY_SLIP = "Salary Slip"
    BANK_STATEMENT = "Bank Statement"
    ITR = "ITR"
    PROPERTY_PAPERS = "Property Papers"
    BUSINESS_REGISTRATION = "Business Registration"
    GST_CERTIFICATE = "GST Certificate"
    PASSPORT = "Passport"
    DRIVING_LICENCE = "Driving Licence"
    PHOTO = "Photo"
    SIGNATURE = "Signature"
    LOAN_APPLICATION_FORM = "Loan Application Form"
    INCOME_PROOF = "Income Proof"
    ADDRESS_PROOF = "Address Proof"
    OTHER = "Other"

    # Added for loan-type-scoped document checklists (phase2.txt)
    FORM16 = "Form 16"
    SALE_AGREEMENT = "Sale Agreement"
    PROPERTY_VALUATION_REPORT = "Property Valuation Report"
    PROPERTY_TAX_RECEIPT = "Property Tax Receipt"
    ENCUMBRANCE_CERTIFICATE = "Encumbrance Certificate"
    OCCUPANCY_CERTIFICATE = "Occupancy Certificate"
    SALE_DEED = "Sale Deed"
    EMPLOYEE_ID = "Employee ID"
    UDYAM_CERTIFICATE = "Udyam Certificate"
    SHOP_LICENSE = "Shop License"
    PARTNERSHIP_DEED = "Partnership Deed"
    MOA = "MOA"
    AOA = "AOA"
    CIN_CERTIFICATE = "CIN Certificate"
    BALANCE_SHEET = "Balance Sheet"
    PROFIT_LOSS_STATEMENT = "Profit & Loss Statement"
    GST_RETURNS = "GST Returns"
    AUDIT_REPORT = "Audit Report"


class DocumentStatus(str, enum.Enum):
    UPLOADED = "Uploaded"
    VERIFIED = "Verified"
    REJECTED = "Rejected"
