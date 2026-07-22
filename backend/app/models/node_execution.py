import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class NodeExecution(Base):
    __tablename__ = "node_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_execution_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    node_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Float, nullable=True)
    error_category = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_attempt = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
