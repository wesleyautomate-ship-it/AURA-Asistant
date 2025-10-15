from fastapi import APIRouter
from datetime import datetime
from app.core.database import check_db_connection

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_v1():
    db_ok = check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "version": "v1",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "dependencies": {"database": "ok" if db_ok else "down"},
    }
