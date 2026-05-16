"""
LangGraph graph builder.
Assembles the Orchestrator and Agent nodes.
"""
import logging
from typing import Literal
from langgraph.graph import StateGraph, END

from backend.graph.state import AgentState
from backend.agents.orchestrator import intent_classifier_node
from backend.agents.order_agent import order_agent_node
from backend.agents.refund_agent import refund_agent_node
from backend.agents.faq_agent import faq_agent_node
from backend.agents.escalation_agent import escalation_agent_node

logger = logging.getLogger(__name__)

def route_after_intent(state: AgentState) -> str:
    """
    Conditional edge routing logic based on intent classification.
    """
    if state.get("escalated") or state.get("confidence", 1.0) < 0.4:
        logger.info("[Router] Routing to: escalation_agent (Low confidence or forced)")
        return "escalation_agent"
        
    intent = state.get("intent", "general")
    
    routes = {
        "order_tracking": "order_agent",
        "refund_request": "refund_agent",
        "faq": "faq_agent",
        "general": "faq_agent",
        "complaint": "escalation_agent",
    }
    
    target = routes.get(intent, "faq_agent")
    logger.info(f"[Router] Intent '{intent}' routing to: {target}")
    return target


def build_graph():
    """Constructs and compiles the LangGraph workflow."""
    
    workflow = StateGraph(AgentState)
    
    # 1. Add Nodes
    workflow.add_node("intent_classifier", intent_classifier_node)
    workflow.add_node("order_agent", order_agent_node)
    workflow.add_node("refund_agent", refund_agent_node)
    workflow.add_node("faq_agent", faq_agent_node)
    workflow.add_node("escalation_agent", escalation_agent_node)
    
    # 2. Define Edges
    workflow.set_entry_point("intent_classifier")
    
    # Routing from orchestrator to specialized agents
    workflow.add_conditional_edges(
        "intent_classifier",
        route_after_intent,
        {
            "order_agent": "order_agent",
            "refund_agent": "refund_agent",
            "faq_agent": "faq_agent",
            "escalation_agent": "escalation_agent"
        }
    )
    
    # In Phase 3, agents just end the graph (we'll add a synthesizer in later phases if needed, 
    # but for now, they go to END).
    workflow.add_edge("order_agent", END)
    workflow.add_edge("refund_agent", END)
    workflow.add_edge("faq_agent", END)
    workflow.add_edge("escalation_agent", END)
    
    return workflow.compile()

# Singleton compiled graph
compiled_graph = build_graph()
