import uuid

from sqlalchemy.orm import Session

from app.models.enums import DocumentStatus
from app.models.loan_document import LoanDocument
from app.schemas.loan_document import LoanDocumentCreate


def create_document(db: Session, data: LoanDocumentCreate) -> LoanDocument:
    document = LoanDocument(**data.model_dump(), status=DocumentStatus.UPLOADED)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def list_documents_for_loan(db: Session, loan_id: uuid.UUID) -> list[LoanDocument]:
    return (
        db.query(LoanDocument)
        .filter(LoanDocument.loan_application_id == loan_id)
        .all()
    )
