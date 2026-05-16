"""
Tools for the Order Tracking Agent.
"""
import json
from langchain_core.tools import tool
from sqlalchemy import select
from backend.database.session import AsyncSessionLocal
from backend.database.models import Order

@tool
async def lookup_order(order_id: str) -> str:
    """Lookup an order by its ID (e.g. ORD-1001) to get its status and details."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        
        if not order:
            return f"Order {order_id} not found."
            
        return json.dumps({
            "id": order.id,
            "status": order.status,
            "total_amount": order.total_amount,
            "tracking_number": order.tracking_number,
            "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None,
            "items": order.items
        })

@tool
async def track_shipment(tracking_number: str) -> str:
    """Get detailed tracking information using a tracking number."""
    if not tracking_number:
        return "No tracking number provided."
        
    # Mocking actual tracking API
    return f"Tracking {tracking_number}: Shipment is in transit. Last scanned at regional hub."

@tool
async def cancel_order(order_id: str) -> str:
    """Attempt to cancel an order by its ID."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        
        if not order:
            return f"Order {order_id} not found."
            
        if order.status in ["shipped", "delivered"]:
            return f"Order {order_id} cannot be canceled because it is already {order.status}."
            
        order.status = "canceled"
        await session.commit()
        
        return f"Order {order_id} has been successfully canceled."
