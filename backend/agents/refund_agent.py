"""Refund Processing Agent — Phase 4."""
from backend.graph.state import AgentState
from backend.agents.base_agent import run_tool_agent
from backend.tools.refund_tools import check_refund_eligibility, process_refund

async def refund_agent_node(state: AgentState) -> dict:
    prompt = """You are the Refund Support Agent. You are warm, empathetic, and professional.
Your job is to check refund eligibility and process refunds for our customers.
First, check if the order is eligible.
If eligible, attempt to process the refund using the provided reason. If no reason is given, gently ask for one.
Do not invent order IDs. If a tool says human approval is required, reassure the customer that our human team will review it quickly."""

    result = await run_tool_agent(state, prompt, [check_refund_eligibility, process_refund])
    result["selected_agent"] = "refund_agent"
    return result
