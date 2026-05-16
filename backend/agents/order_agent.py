"""Order Tracking Agent — Phase 4."""
from backend.graph.state import AgentState
from backend.agents.base_agent import run_tool_agent
from backend.tools.order_tools import lookup_order, track_shipment, cancel_order

async def order_agent_node(state: AgentState) -> dict:
    prompt = """You are the Order Tracking Agent.
Your job is to look up orders, track shipments, and cancel orders if requested.
Be polite and helpful. If the order is not found, apologize.
Always provide the tracking status if available."""

    result = await run_tool_agent(state, prompt, [lookup_order, track_shipment, cancel_order])
    result["selected_agent"] = "order_agent"
    return result
