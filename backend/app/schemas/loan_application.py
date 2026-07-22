import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import LoanStatus, LoanType


class LoanApplicationCreate(BaseModel):
    customer_id: uuid.UUID
    loan_type: LoanType
    requested_amount: Decimal
    loan_purpose: Optional[str] = None
    employment_type: Optional[str] = None
    monthly_income: Optional[Decimal] = None
    employer: Optional[str] = None
    tenure: Optional[int] = None
    interest_rate: Optional[Decimal] = None
    branch: Optional[str] = None
    credit_score: Optional[int] = None
    existing_emi: Optional[Decimal] = None
    property_value: Optional[Decimal] = None
    down_payment: Optional[Decimal] = None
    employment_experience_years: Optional[int] = None
    existing_loan_outstanding: Optional[Decimal] = None
    bank_name: Optional[str] = None
    monthly_household_expenses: Optional[Decimal] = None


class LoanApplicationSubmit(BaseModel):
    changed_by: Optional[str] = None
    notes: Optional[str] = None


class LoanApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_id: uuid.UUID
    loan_type: LoanType
    requested_amount: Decimal
    loan_purpose: Optional[str] = None
    employment_type: Optional[str] = None
    monthly_income: Optional[Decimal] = None
    employer: Optional[str] = None
    tenure: Optional[int] = None
    interest_rate: Optional[Decimal] = None
    branch: Optional[str] = None
    credit_score: Optional[int] = None
    existing_emi: Optional[Decimal] = None
    property_value: Optional[Decimal] = None
    down_payment: Optional[Decimal] = None
    employment_experience_years: Optional[int] = None
    existing_loan_outstanding: Optional[Decimal] = None
    bank_name: Optional[str] = None
    monthly_household_expenses: Optional[Decimal] = None
    status: LoanStatus
    created_at: datetime
    updated_at: datetime
