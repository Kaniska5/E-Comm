"""
Refund routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from backend.database.session import get_db
from backend.schemas.refund import RefundRequest

router = APIRouter(prefix="/refund", tags=["Refunds"])

@router.post("")
async def process_refund(request: RefundRequest, db: AsyncSession = Depends(get_db)) -> Dict:
    """
    Process a manual refund request.
    (Stub implementation for Phase 2)
    """
    return {
        "status": "success",
        "message": f"Refund of {request.amount} for order {request.order_id} requested.",
        "requires_approval": request.amount > 1000.0
    }
