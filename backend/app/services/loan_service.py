import uuid

from sqlalchemy.orm import Session

from app.models.enums import LoanStatus
from app.models.loan_application import LoanApplication
from app.models.loan_status_history import LoanStatusHistory
from app.schemas.loan_application import LoanApplicationCreate, LoanApplicationSubmit


class InvalidLoanStatusTransitionError(Exception):
    pass


def create_loan_application(db: Session, data: LoanApplicationCreate) -> LoanApplication:
    loan_application = LoanApplication(**data.model_dump(), status=LoanStatus.DRAFT)
    db.add(loan_application)
    db.commit()
    db.refresh(loan_application)
    return loan_application


def get_loan_application(db: Session, loan_id: uuid.UUID) -> LoanApplication | None:
    return db.query(LoanApplication).filter(LoanApplication.id == loan_id).first()


def submit_loan_application(
    db: Session, loan: LoanApplication, data: LoanApplicationSubmit
) -> LoanApplication:
    if loan.status != LoanStatus.DRAFT:
        raise InvalidLoanStatusTransitionError(
            f"Loan application is already {loan.status.value}, cannot submit again"
        )

    history = LoanStatusHistory(
        loan_application_id=loan.id,
        previous_status=loan.status,
        new_status=LoanStatus.DOCUMENTS_UPLOADED,
        changed_by=data.changed_by,
        notes=data.notes,
    )
    loan.status = LoanStatus.DOCUMENTS_UPLOADED
    db.add(history)
    db.commit()
    db.refresh(loan)
    return loan
