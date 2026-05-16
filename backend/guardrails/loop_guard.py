"""
Loop Prevention Guardrail — Phase 5.
"""
from backend.graph.state import AgentState
from backend.config.settings import settings

def check_loop_limit(state: AgentState) -> bool:
    """
    Check if the workflow has exceeded the maximum allowed retries/loops.
    Returns True if safe to continue, False if escalation is required.
    """
    retry_count = state.get("retry_count", 0)
    
    if retry_count >= settings.MAX_AGENT_RETRIES:
        return False
        
    return True
