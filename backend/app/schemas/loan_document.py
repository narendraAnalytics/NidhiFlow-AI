import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import DocumentStatus, DocumentType


class LoanDocumentCreate(BaseModel):
    loan_application_id: uuid.UUID
    document_name: str
    document_type: DocumentType
    firebase_url: Optional[str] = None
    uploaded_by: Optional[str] = None


class LoanDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    loan_application_id: uuid.UUID
    document_name: str
    document_type: DocumentType
    firebase_url: Optional[str] = None
    upload_time: datetime
    uploaded_by: Optional[str] = None
    status: DocumentStatus
