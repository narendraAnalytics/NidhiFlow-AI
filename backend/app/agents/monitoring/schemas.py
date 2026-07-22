from typing import Literal, Optional

from pydantic import BaseModel


class NodeTelemetryRecord(BaseModel):
    node_name: str
    status: Literal["completed", "failed"]
    started_at: str
    finished_at: str
    duration: float
    error_category: Optional[str] = None
    error_message: Optional[str] = None
    retry_attempt: int = 0
