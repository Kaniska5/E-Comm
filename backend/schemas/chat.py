"""
Pydantic schemas for Chat.
"""
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "Where is my order?"})
    session_id: str = Field(..., json_schema_extra={"example": "sess-1234"})
    customer_id: str | None = Field(default=None, json_schema_extra={"example": "CUST-001"})

class ChatResponse(BaseModel):
    response: str
    intent: str | None = None
    confidence: float | None = None
    escalated: bool = False
    requires_human_approval: bool = False
    approval_id: str | None = None
    session_id: str
