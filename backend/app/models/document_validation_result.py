import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class DocumentValidationResult(Base):
    __tablename__ = "document_validation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("loan_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_type = Column(String, nullable=True)
    extracted_fields = Column(JSONB, nullable=True)
    detected_document_type = Column(String, nullable=True)
    type_match_status = Column(String, nullable=True)
    processing_status = Column(String, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("LoanDocument")
