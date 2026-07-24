from typing import Literal

from pydantic import BaseModel

IntakeStatus = Literal["passed", "failed"]


class IntakeSummary(BaseModel):
    status: IntakeStatus
    missing_documents: list[str]
    missing_form_fields: list[str]
    warnings: list[str]
