import logging

import psycopg2
from fastapi import APIRouter, HTTPException

from app.core.config import DATABASE_URL

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health/db")
def health_db():
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=5)
        conn.cursor().execute("SELECT 1")
        conn.close()
    except Exception:
        logger.exception("DB health check failed")
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ok", "database": "connected"}
