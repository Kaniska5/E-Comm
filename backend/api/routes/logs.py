"""
Logs routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from backend.database.session import get_db
from backend.database.models import AuditLog

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.get("")
async def get_logs(limit: int = 100, db: AsyncSession = Depends(get_db)) -> List[Dict]:
    """
    Fetch recent audit logs.
    """
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    )
    logs = result.scalars().all()
    
    # Simple dict serialization for now
    return [
        {
            "id": log.id,
            "session_id": log.session_id,
            "event_type": log.event_type,
            "details": log.details,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]
