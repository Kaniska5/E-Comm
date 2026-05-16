"""FAQ Agent — Phase 4."""
from backend.graph.state import AgentState
from backend.agents.base_agent import run_tool_agent
from backend.tools.faq_tools import search_faq

async def faq_agent_node(state: AgentState) -> dict:
    prompt = """You are the FAQ Support Agent.
Your job is to answer customer questions using the company policies and FAQ.
Do not invent answers. If the policy does not explicitly cover their question,
politely inform them that you do not have that information.
Keep your answers clear, concise, and helpful."""

    result = await run_tool_agent(state, prompt, [search_faq])
    result["selected_agent"] = "faq_agent"
    return result
