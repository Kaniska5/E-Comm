"""
Pydantic schemas for Human Approvals.
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ApprovalResponse(BaseModel):
    id: str
    session_id: str
    action_type: str
    details: dict
    status: str
    reviewer_notes: str | None
    created_at: datetime
    resolved_at: datetime | None
    
    model_config = ConfigDict(from_attributes=True)

class ApprovalActionRequest(BaseModel):
    notes: str | None = None
