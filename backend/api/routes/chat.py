"""
Chat routes - Entry point for LangGraph Orchestrator.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from backend.database.session import get_db
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.graph.builder import compiled_graph
from backend.monitoring.audit_logger import log_event_async

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

# Simple in-memory session store mapping session_id to chat_history
SESSION_STORE = {}

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Process a customer query via the Agentic AI Pipeline.
    """
    session_id = request.session_id
    
    # Initialize session history if it doesn't exist
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = []
        
    chat_history = SESSION_STORE[session_id]
    
    initial_state = {
        "session_id": session_id,
        "customer_id": request.customer_id,
        "query": request.query,
        "chat_history": chat_history.copy(), # Pass a copy to avoid unintended mutations
        "retry_count": 0,
        "max_retries": 2,
    }
    
    try:
        # LangGraph execution
        final_state = await compiled_graph.ainvoke(initial_state)
        final_response_text = final_state.get("final_response", "No response generated.")
        
        # Update session history
        SESSION_STORE[session_id].append({"role": "user", "content": request.query})
        SESSION_STORE[session_id].append({"role": "assistant", "content": final_response_text})
        
        # Phase 7: Audit Logging
        await log_event_async(
            session_id=session_id,
            event_type="chat_interaction",
            details={
                "query": request.query,
                "intent": final_state.get("intent"),
                "selected_agent": final_state.get("selected_agent"),
                "requires_approval": final_state.get("requires_human_approval", False),
                "escalated": final_state.get("escalated", False)
            }
        )
        
        return ChatResponse(
            response=final_response_text,
            intent=final_state.get("intent", "general"),
            confidence=final_state.get("confidence", 0.0),
            escalated=final_state.get("escalated", False),
            requires_human_approval=final_state.get("requires_human_approval", False),
            approval_id=final_state.get("approval_id"),
            session_id=final_state.get("session_id", request.session_id)
        )
    except Exception as e:
        logger.error(f"Error during LangGraph execution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during chat processing.")

