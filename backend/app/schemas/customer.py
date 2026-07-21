import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    pan: str
    aadhaar: str
    address: Optional[str] = None


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: EmailStr
    phone: str
    pan: str
    aadhaar: str
    address: Optional[str] = None
    created_at: datetime
    updated_at: datetime
