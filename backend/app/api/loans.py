import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.loan_application import LoanApplicationCreate, LoanApplicationResponse
from app.services.loan_service import create_loan_application, get_loan_application

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
