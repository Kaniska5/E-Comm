"""
Base helper for running agent nodes with tool calling.
"""
from typing import List, Callable
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from backend.agents.llm import get_llm
from backend.graph.state import AgentState

def extract_text(content) -> str:
    """Helper to safely extract string from AIMessage content which can sometimes be a list."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                texts.append(block["text"])
            elif isinstance(block, str):
                texts.append(block)
        return " ".join(texts)
    return str(content)

async def run_tool_agent(state: AgentState, system_prompt: str, tools: List[Callable]) -> dict:
    """Helper to run a simple ReAct-style loop inside a node."""
    llm = get_llm(temperature=0.0)
    llm_with_tools = llm.bind_tools(tools)
    
    messages = [SystemMessage(content=system_prompt)]
    
    # Add history
    for msg in state.get("chat_history", []):
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            # Simplification: just using AI message content, ignoring tool history in past turns
            messages.append(SystemMessage(content=f"Previous assistant: {msg['content']}"))
            
    messages.append(HumanMessage(content=state.get("query", "")))
    
    # Single loop tool execution
    reasoning_steps = state.get("reasoning_steps", [])
    
    response = await llm_with_tools.ainvoke(messages)
    
    # If no tool calls, it synthesized a response
    if not response.tool_calls:
        return {"final_response": extract_text(response.content)}
        
    messages.append(response)
    
    # Execute tools
    tool_map = {tool.name: tool for tool in tools}
    tool_calls_record = state.get("tool_calls", [])
    
    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # Inject session_id if tool needs it (like process_refund)
        if "session_id" in tool_args and not tool_args.get("session_id"):
             tool_args["session_id"] = state.get("session_id")
        elif tool_name == "process_refund":
             tool_args["session_id"] = state.get("session_id")
             
        reasoning_steps.append(f"Tool Call: {tool_name} with args {tool_args}")
        tool_calls_record.append({"name": tool_name, "args": tool_args})
        
        tool_instance = tool_map.get(tool_name)
        if not tool_instance:
             reasoning_steps.append(f"Tool Error: Hallucinated tool {tool_name}")
             tool_result = f"Error: You do not have access to a tool named '{tool_name}'."
        else:
             tool_result = await tool_instance.ainvoke(tool_args)
        
        reasoning_steps.append(f"Tool Output: {tool_result}")
        messages.append(ToolMessage(tool_call_id=tool_call["id"], content=str(tool_result), name=tool_name))
        
    # Second LLM call to synthesize the final response based on tool outputs
    final_response = await llm.ainvoke(messages) # We don't bind tools again to force synthesis
    
    # Check for approval triggers
    requires_approval = any("GUARDRAIL BLOCKED" in msg.content for msg in messages if isinstance(msg, ToolMessage))
    approval_id = None
    if requires_approval:
        for msg in messages:
            if isinstance(msg, ToolMessage) and "ID: APP-" in msg.content:
                parts = msg.content.split("ID: ")
                if len(parts) > 1:
                    approval_id = parts[1].split(")")[0]
                    
    return {
        "final_response": extract_text(final_response.content),
        "reasoning_steps": reasoning_steps,
        "tool_calls": tool_calls_record,
        "requires_human_approval": requires_approval,
        "approval_id": approval_id
    }
