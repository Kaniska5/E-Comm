"""
API Tests for Phase 2 endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from backend.main import app
from backend.database.session import AsyncSessionLocal
from backend.database.models import Customer, Order

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_get_order_not_found():
    # Because db is initialized in lifespan, we use lifespan context for the tests 
    # to ensure seed data is available and DB is created.
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/orders/nonexistent")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_chat_endpoint(monkeypatch):
    # Mock the LangGraph execution
    async def mock_ainvoke(*args, **kwargs):
        return {
            "final_response": "Mocked response",
            "intent": "order_tracking",
            "confidence": 0.95,
            "session_id": "sess-123"
        }
        
    from backend.api.routes import chat
    monkeypatch.setattr(chat.compiled_graph, "ainvoke", mock_ainvoke)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/chat", json={
            "query": "Where is my order?",
            "session_id": "sess-123"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Mocked response"
    assert data["intent"] == "order_tracking"
    assert data["session_id"] == "sess-123"

@pytest.mark.asyncio
async def test_refund_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/refund", json={
            "order_id": "ORD-1001",
            "amount": 1500.0,
            "reason": "Defective item"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["requires_approval"] is True
