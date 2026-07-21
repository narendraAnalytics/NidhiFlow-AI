import uuid

from sqlalchemy.orm import Session

from app.models.enums import LoanStatus
from app.models.loan_application import LoanApplication
from app.schemas.loan_application import LoanApplicationCreate


def create_loan_application(db: Session, data: LoanApplicationCreate) -> LoanApplication:
    loan_application = LoanApplication(**data.model_dump(), status=LoanStatus.DRAFT)
    db.add(loan_application)
    db.commit()
    db.refresh(loan_application)
    return loan_application


def get_loan_application(db: Session, loan_id: uuid.UUID) -> LoanApplication | None:
    return db.query(LoanApplication).filter(LoanApplication.id == loan_id).first()
