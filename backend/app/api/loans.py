import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.loan_application import (
    LoanApplicationCreate,
    LoanApplicationResponse,
    LoanApplicationSubmit,
)
from app.services.loan_service import (
    InvalidLoanStatusTransitionError,
    create_loan_application,
    get_loan_application,
    submit_loan_application,
)

router = APIRouter(prefix="/loan", tags=["loans"])


@router.post("", response_model=LoanApplicationResponse, status_code=201)
def create_loan_application_route(data: LoanApplicationCreate, db: Session = Depends(get_db)):
    return create_loan_application(db, data)


@router.get("/{loan_id}", response_model=LoanApplicationResponse)
def get_loan_application_route(loan_id: uuid.UUID, db: Session = Depends(get_db)):
    loan_application = get_loan_application(db, loan_id)
    if loan_application is None:
        raise HTTPException(status_code=404, detail="Loan application not found")
    return loan_application


@router.post("/{loan_id}/submit", response_model=LoanApplicationResponse)
def submit_loan_application_route(
    loan_id: uuid.UUID, data: LoanApplicationSubmit, db: Session = Depends(get_db)
):
    loan_application = get_loan_application(db, loan_id)
    if loan_application is None:
        raise HTTPException(status_code=404, detail="Loan application not found")
    try:
        return submit_loan_application(db, loan_application, data)
    except InvalidLoanStatusTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
