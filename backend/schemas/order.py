"""
Pydantic schemas for Orders.
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class OrderItem(BaseModel):
    name: str
    price: float
    quantity: int

class OrderResponse(BaseModel):
    id: str
    customer_id: str
    status: str
    total_amount: float
    items: list[OrderItem] | list[dict]
    tracking_number: str | None
    estimated_delivery: datetime | None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
