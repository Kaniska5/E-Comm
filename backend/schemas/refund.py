"""
Pydantic schemas for Refunds.
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class RefundRequest(BaseModel):
    order_id: str
    amount: float
    reason: str

class RefundResponse(BaseModel):
    id: str
    order_id: str
    amount: float
    reason: str
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
