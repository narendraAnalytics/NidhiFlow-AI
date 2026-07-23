import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
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
    credit_score = Column(Integer, nullable=True)
    existing_emi = Column(Numeric(14, 2), nullable=True)
    property_value = Column(Numeric(14, 2), nullable=True)
    down_payment = Column(Numeric(14, 2), nullable=True)
    employment_experience_years = Column(Integer, nullable=True)
    existing_loan_outstanding = Column(Numeric(14, 2), nullable=True)
    bank_name = Column(String, nullable=True)
    monthly_household_expenses = Column(Numeric(14, 2), nullable=True)
    business_name = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    business_vintage_years = Column(Integer, nullable=True)
    annual_turnover = Column(Numeric(14, 2), nullable=True)
    monthly_business_revenue = Column(Numeric(14, 2), nullable=True)
    monthly_net_profit = Column(Numeric(14, 2), nullable=True)
    gst_number = Column(String, nullable=True)
    udyam_registration_number = Column(String, nullable=True)
    cin_llpin = Column(String, nullable=True)
    number_of_employees = Column(Integer, nullable=True)
    existing_business_loan_outstanding = Column(Numeric(14, 2), nullable=True)
    business_bank_name = Column(String, nullable=True)
    collateral_required = Column(Boolean, nullable=True)
    collateral_type = Column(String, nullable=True)
    collateral_value = Column(Numeric(14, 2), nullable=True)
    occupation_designation = Column(String, nullable=True)
    total_work_experience = Column(String, nullable=True)
    experience_current_employer = Column(String, nullable=True)
    property_type = Column(String, nullable=True)
    property_status = Column(String, nullable=True)
    builder_developer_name = Column(String, nullable=True)
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
