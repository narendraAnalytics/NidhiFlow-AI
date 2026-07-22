from app.agents.pipeline_orchestrator.rules import (
    ERROR_OCR_ERROR,
    ERROR_SYSTEM_ERROR,
    ERROR_VALIDATION_ERROR,
)

# Which error category to attribute to a node's failure, for telemetry
# purposes. Reuses the category constants defined in pipeline_orchestrator
# (single source of truth for error categories).
NODE_ERROR_CATEGORY = {
    "intake_supervisor": ERROR_SYSTEM_ERROR,
    "document_intelligence": ERROR_OCR_ERROR,
    "validation_compliance": ERROR_VALIDATION_ERROR,
    "pipeline_orchestrator": ERROR_SYSTEM_ERROR,
}
