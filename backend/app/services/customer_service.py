import logging
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate

logger = logging.getLogger(__name__)


class CustomerAlreadyExistsError(Exception):
    pass


def create_customer(db: Session, data: CustomerCreate, firebase_uid: str | None = None) -> Customer:
    if firebase_uid is not None:
        existing = get_customer_by_firebase_uid(db, firebase_uid)
        if existing is not None:
            return existing

    customer = Customer(**data.model_dump(), firebase_uid=firebase_uid)
    db.add(customer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.exception("Customer creation failed due to a uniqueness conflict")
        raise CustomerAlreadyExistsError(
            "A customer with this email, PAN, or Aadhaar already exists"
        )
    db.refresh(customer)
    return customer


def get_customer(db: Session, customer_id: uuid.UUID) -> Customer | None:
    return db.query(Customer).filter(Customer.id == customer_id).first()


def get_customer_by_firebase_uid(db: Session, firebase_uid: str) -> Customer | None:
    return db.query(Customer).filter(Customer.firebase_uid == firebase_uid).first()


def list_customers(db: Session, skip: int = 0, limit: int = 100) -> list[Customer]:
    return db.query(Customer).offset(skip).limit(limit).all()
