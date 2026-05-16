"""
Human Approvals routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.database.session import get_db
from backend.database.models import HumanApproval
from backend.schemas.approval import ApprovalResponse, ApprovalActionRequest
from backend.database.models import utcnow

router = APIRouter(prefix="/approvals", tags=["Approvals"])

@router.get("", response_model=List[ApprovalResponse])
async def list_pending_approvals(db: AsyncSession = Depends(get_db)):
    """List all pending human approvals."""
    result = await db.execute(select(HumanApproval).where(HumanApproval.status == "pending"))
    return result.scalars().all()

@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
async def approve_action(
    approval_id: str, 
    request: ApprovalActionRequest, 
    db: AsyncSession = Depends(get_db)
):
    """Approve a pending action."""
    result = await db.execute(select(HumanApproval).where(HumanApproval.id == approval_id))
    approval = result.scalar_one_or_none()
    
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    if approval.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request is already {approval.status}")
        
    approval.status = "approved"
    approval.reviewer_notes = request.notes
    approval.resolved_at = utcnow()
    
    await db.commit()
    await db.refresh(approval)
    return approval

@router.post("/{approval_id}/reject", response_model=ApprovalResponse)
async def reject_action(
    approval_id: str, 
    request: ApprovalActionRequest, 
    db: AsyncSession = Depends(get_db)
):
    """Reject a pending action."""
    result = await db.execute(select(HumanApproval).where(HumanApproval.id == approval_id))
    approval = result.scalar_one_or_none()
    
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    if approval.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request is already {approval.status}")
        
    approval.status = "rejected"
    approval.reviewer_notes = request.notes
    approval.resolved_at = utcnow()
    
    await db.commit()
    await db.refresh(approval)
    return approval
