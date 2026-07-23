from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.firebase_auth import get_current_firebase_user
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.schemas.loan_application import LoanApplicationResponse
from app.services.customer_service import (
    CustomerAlreadyExistsError,
    create_customer,
    get_customer_by_firebase_uid,
    list_customers,
)
from app.services.loan_service import get_active_draft_loan

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer_route(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_firebase_user),
):
    try:
        return create_customer(db, data, firebase_uid=current_user["uid"])
    except CustomerAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("", response_model=list[CustomerResponse])
def list_customers_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return list_customers(db, skip=skip, limit=limit)


@router.get("/me/active-loan", response_model=LoanApplicationResponse | None)
def get_my_active_loan_route(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_firebase_user),
):
    customer = get_customer_by_firebase_uid(db, current_user["uid"])
    if customer is None:
        return None
    return get_active_draft_loan(db, customer.id)
