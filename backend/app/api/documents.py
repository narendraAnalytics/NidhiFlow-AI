import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.loan_document import LoanDocumentCreate, LoanDocumentResponse
from app.services.document_service import create_document, list_documents_for_loan

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=LoanDocumentResponse, status_code=201)
def create_document_route(data: LoanDocumentCreate, db: Session = Depends(get_db)):
    return create_document(db, data)


@router.get("/{loan_id}", response_model=list[LoanDocumentResponse])
def list_documents_route(loan_id: uuid.UUID, db: Session = Depends(get_db)):
    return list_documents_for_loan(db, loan_id)
