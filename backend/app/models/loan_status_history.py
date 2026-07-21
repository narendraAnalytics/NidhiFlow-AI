import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.enums import LoanStatus


class LoanStatusHistory(Base):
    __tablename__ = "loan_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("loan_applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    previous_status = Column(Enum(LoanStatus, name="loan_status"), nullable=True)
    new_status = Column(Enum(LoanStatus, name="loan_status"), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    changed_by = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    loan_application = relationship("LoanApplication", back_populates="status_history")
