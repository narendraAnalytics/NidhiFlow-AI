from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.services.customer_service import CustomerAlreadyExistsError, create_customer, list_customers

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer_route(data: CustomerCreate, db: Session = Depends(get_db)):
    try:
        return create_customer(db, data)
    except CustomerAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("", response_model=list[CustomerResponse])
def list_customers_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return list_customers(db, skip=skip, limit=limit)
