import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.document_checklist import LOAN_TYPE_DOCUMENT_CHECKLIST
from app.core.firebase_auth import get_current_firebase_user, require_owned_loan
from app.schemas.loan_document import LoanDocumentCreate, LoanDocumentResponse
from app.services.document_service import create_document, list_documents_for_loan

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=LoanDocumentResponse, status_code=201)
def create_document_route(
    data: LoanDocumentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_firebase_user),
):
    loan = require_owned_loan(db, current_user, data.loan_application_id)
    if data.document_type not in LOAN_TYPE_DOCUMENT_CHECKLIST[loan.loan_type]:
        raise HTTPException(
            status_code=400,
            detail=f"'{data.document_type.value}' is not an expected document for a {loan.loan_type.value} loan",
        )
    return create_document(db, data)


@router.get("/{loan_id}", response_model=list[LoanDocumentResponse])
def list_documents_route(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_firebase_user),
):
    require_owned_loan(db, current_user, loan_id)
    return list_documents_for_loan(db, loan_id)
