"""
Tests for specialized agents and guardrails.
"""
import pytest
from backend.graph.state import AgentState
from backend.guardrails.refund_guard import validate_refund_amount
from backend.guardrails.loop_guard import check_loop_limit
from backend.tools.refund_tools import check_refund_eligibility
from backend.config.settings import settings

def test_refund_guard():
    assert validate_refund_amount(500.0) is True
    assert validate_refund_amount(settings.REFUND_AUTO_APPROVE_LIMIT + 100) is False

def test_loop_guard():
    state = AgentState(retry_count=1)
    assert check_loop_limit(state) is True
    
    state["retry_count"] = settings.MAX_AGENT_RETRIES + 1
    assert check_loop_limit(state) is False

@pytest.mark.asyncio
async def test_refund_tool_guardrail_db(setup_test_db):
    """Test process_refund directly to see if HITL works."""
    from backend.tools.refund_tools import process_refund
    
    # Under limit -> auto approve
    res1 = await process_refund.ainvoke({"order_id": "ORD-1002", "amount": 500.0, "reason": "Test", "session_id": "sess-test"})
    assert "SUCCESS" in res1
    
    # Over limit -> HITL
    res2 = await process_refund.ainvoke({"order_id": "ORD-1002", "amount": 1500.0, "reason": "Test high", "session_id": "sess-test-2"})
    assert "GUARDRAIL BLOCKED" in res2
    assert "APP-" in res2
