import uuid

from fastapi import Header, HTTPException
from firebase_admin import auth as firebase_auth
from sqlalchemy.orm import Session

from app.core.firebase_app import get_firebase_app


def get_current_firebase_user(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    get_firebase_app()
    try:
        decoded = firebase_auth.verify_id_token(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired ID token") from exc
    return {"uid": decoded["uid"], "email": decoded.get("email")}


def require_owned_customer_id(db: Session, current_user: dict, customer_id: uuid.UUID) -> None:
    """Raise 403 unless customer_id belongs to the calling Firebase user."""
    from app.services.customer_service import get_customer_by_firebase_uid

    customer = get_customer_by_firebase_uid(db, current_user["uid"])
    if customer is None or customer.id != customer_id:
        raise HTTPException(status_code=403, detail="Not authorized for this customer")


def require_owned_loan(db: Session, current_user: dict, loan_id: uuid.UUID):
    """Raise 404/403 unless loan_id exists and belongs to the calling Firebase user; returns the loan."""
    from app.services.loan_service import get_loan_application

    loan = get_loan_application(db, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan application not found")
    require_owned_customer_id(db, current_user, loan.customer_id)
    return loan
