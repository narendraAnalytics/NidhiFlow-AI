import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class LoanValidationSummary(Base):
    __tablename__ = "loan_validation_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("loan_applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    validation_status = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    missing_documents = Column(JSONB, nullable=False)
    field_mismatches = Column(JSONB, nullable=False)
    warnings = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    loan_application = relationship("LoanApplication")
