from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.monitoring import WorkflowHealthResponse
from app.services.monitoring_service import get_workflow_health

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/health", response_model=WorkflowHealthResponse)
def get_workflow_health_route(db: Session = Depends(get_db)):
    return get_workflow_health(db)
