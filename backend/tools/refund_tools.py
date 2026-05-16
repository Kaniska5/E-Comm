"""
Tools for the Refund Agent, including guardrail integration.
"""
import uuid
from langchain_core.tools import tool
from sqlalchemy import select
from backend.database.session import AsyncSessionLocal
from backend.database.models import Order, Refund, HumanApproval, utcnow
from backend.config.settings import settings

@tool
async def check_refund_eligibility(order_id: str) -> str:
    """Check if an order is eligible for a refund (must be within 10 days of creation)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        
        if not order:
            return f"Order {order_id} not found."
            
        days_since = (utcnow() - order.created_at).days
        if days_since > 10:
            return f"Order {order_id} is {days_since} days old. It exceeds the 10-day return policy."
            
        return f"Order {order_id} is eligible for a refund. Total amount: {order.total_amount}."

@tool
async def process_refund(order_id: str, amount: float, reason: str, session_id: str) -> str:
    """
    Attempt to process a refund.
    Applies the guardrail check (Phase 5 & 6) before executing.
    """
    from backend.guardrails.refund_guard import validate_refund_amount
    
    async with AsyncSessionLocal() as session:
        # Guardrail check using the imported guard
        if not validate_refund_amount(amount):
            # Trigger HITL
            approval_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
            approval = HumanApproval(
                id=approval_id,
                session_id=session_id,
                action_type="refund",
                details={"order_id": order_id, "amount": amount, "reason": reason},
                status="pending"
            )
            session.add(approval)
            await session.commit()
            
            return f"GUARDRAIL BLOCKED: Refund of {amount} exceeds auto-approve limit of {settings.REFUND_AUTO_APPROVE_LIMIT}. Human approval requested (ID: {approval_id}). Please inform the customer."
        
        # Auto-approve
        refund_id = f"REF-{uuid.uuid4().hex[:8].upper()}"
        refund = Refund(
            id=refund_id,
            order_id=order_id,
            amount=amount,
            reason=reason,
            status="approved"
        )
        session.add(refund)
        await session.commit()
        
        return f"SUCCESS: Refund of {amount} processed automatically (ID: {refund_id})."
