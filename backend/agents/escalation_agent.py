"""Human Escalation Agent — Phase 4."""
import uuid
from backend.graph.state import AgentState
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import AsyncSessionLocal
from backend.database.models import EscalationTicket
import logging

logger = logging.getLogger(__name__)

async def escalation_agent_node(state: AgentState) -> dict:
    """
    Workflow agent. Not a reasoning LLM.
    Generates a ticket and escalates to a human.
    """
    session_id = state.get("session_id")
    customer_id = state.get("customer_id")
    reason = state.get("escalation_reason") or state.get("query")
    
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    
    logger.info(f"Escalating session {session_id}. Ticket: {ticket_id}")
    
    async with AsyncSessionLocal() as session:
        ticket = EscalationTicket(
            id=ticket_id,
            session_id=session_id,
            customer_id=customer_id,
            reason=reason,
            status="open"
        )
        session.add(ticket)
        await session.commit()
        
    final_response = (
        f"I'm sorry, I'm unable to fully resolve your issue at this time. "
        f"I have escalated this to our human support team. "
        f"Your ticket number is {ticket_id}. "
        f"An agent will review it and get back to you shortly."
    )
    
    return {
        "final_response": final_response,
        "selected_agent": "escalation_agent",
        "escalated": True,
        "reasoning_steps": state.get("reasoning_steps", []) + [f"Escalated to human. Ticket {ticket_id} created."]
    }
