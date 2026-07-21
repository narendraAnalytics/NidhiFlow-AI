from app.schemas.customer import CustomerCreate, CustomerResponse
from app.schemas.loan_application import (
    LoanApplicationCreate,
    LoanApplicationResponse,
    LoanApplicationSubmit,
)
from app.schemas.loan_document import LoanDocumentCreate, LoanDocumentResponse

__all__ = [
    "CustomerCreate",
    "CustomerResponse",
    "LoanApplicationCreate",
    "LoanApplicationResponse",
    "LoanApplicationSubmit",
    "LoanDocumentCreate",
    "LoanDocumentResponse",
]
