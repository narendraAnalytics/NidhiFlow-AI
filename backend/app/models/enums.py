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


class DocumentStatus(str, enum.Enum):
    UPLOADED = "Uploaded"
    VERIFIED = "Verified"
    REJECTED = "Rejected"
