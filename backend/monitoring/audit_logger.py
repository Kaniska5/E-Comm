"""
Audit Logger - Phase 7.
Logs interactions securely to the local SQLite DB.
"""
from backend.database.session import AsyncSessionLocal
from backend.database.models import AuditLog
import logging

logger = logging.getLogger(__name__)

async def log_event_async(session_id: str, event_type: str, details: dict):
    """
    Writes an event into the audit_logs table.
    """
    try:
        async with AsyncSessionLocal() as session:
            log_entry = AuditLog(
                session_id=session_id,
                event_type=event_type,
                details=details
            )
            session.add(log_entry)
            await session.commit()
    except Exception as e:
        logger.error(f"Failed to write audit log for session {session_id}: {e}")
