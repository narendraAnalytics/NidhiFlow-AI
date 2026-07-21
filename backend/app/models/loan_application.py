import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.enums import LoanStatus, LoanType


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    loan_type = Column(Enum(LoanType, name="loan_type"), nullable=False)
    requested_amount = Column(Numeric(14, 2), nullable=False)
    loan_purpose = Column(Text, nullable=True)
    employment_type = Column(String, nullable=True)
    monthly_income = Column(Numeric(14, 2), nullable=True)
    employer = Column(String, nullable=True)
    tenure = Column(Integer, nullable=True)
    interest_rate = Column(Numeric(5, 2), nullable=True)
    branch = Column(String, nullable=True)
    status = Column(Enum(LoanStatus, name="loan_status"), nullable=False, default=LoanStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="loan_applications")
    documents = relationship(
        "LoanDocument", back_populates="loan_application", cascade="all, delete-orphan"
    )
    status_history = relationship(
        "LoanStatusHistory", back_populates="loan_application", cascade="all, delete-orphan"
    )
