"""
Orchestrator Agent — specifically the Intent Classification Node.
"""
import logging
import json
from typing import Literal
from pydantic import BaseModel, Field

from backend.graph.state import AgentState
from backend.agents.llm import get_llm
from backend.config.settings import settings

logger = logging.getLogger(__name__)

# Output schema for the structured LLM response
class IntentClassification(BaseModel):
    intent: Literal["order_tracking", "refund_request", "faq", "complaint", "general"] = Field(
        description="The classified intent of the customer query."
    )
    confidence: float = Field(
        description="Confidence score from 0.0 to 1.0", 
        ge=0.0, le=1.0
    )
    reasoning: str = Field(
        description="Brief explanation of why this intent was chosen."
    )

async def intent_classifier_node(state: AgentState) -> dict:
    """
    Analyzes the user's query and classifies the intent to route to the proper agent.
    Returns partial state updates.
    """
    query = state.get("query", "")
    retry_count = state.get("retry_count", 0)
    
    logger.info(f"Classifying intent for query: {query}")
    
    # If retries exceeded, force escalation
    if retry_count >= settings.MAX_AGENT_RETRIES:
        logger.warning(f"Retry limit ({settings.MAX_AGENT_RETRIES}) reached. Escalating.")
        return {
            "intent": "complaint",
            "confidence": 1.0,
            "escalated": True,
            "escalation_reason": "Max retries exceeded.",
            "reasoning_steps": state.get("reasoning_steps", []) + ["Forced escalation due to retry limit."]
        }
        
    llm = get_llm(temperature=0.0)
    
    # Not all models natively support `.with_structured_output` perfectly,
    # but Gemini and OpenAI usually do.
    structured_llm = llm.with_structured_output(IntentClassification)
    
    prompt = f"""You are the Orchestrator for an E-commerce Customer Support AI.
Your job is to classify the intent of the customer's query.

Available Intents:
- order_tracking: Query about order status, delivery, ETA, or tracking.
- refund_request: Query asking for a refund, return, or money back.
- faq: General policy questions (shipping, returns, payments, coupons).
- complaint: Expressing deep frustration, legal threats, or demanding human escalation.
- general: Any other query.

Query: "{query}"

Classify the intent strictly according to the schema.
"""

    try:
        result: IntentClassification = await structured_llm.ainvoke(prompt)
        
        reasoning_step = f"Intent classified as '{result.intent}' (confidence: {result.confidence:.2f}): {result.reasoning}"
        logger.info(reasoning_step)
        
        return {
            "intent": result.intent,
            "confidence": result.confidence,
            "reasoning_steps": state.get("reasoning_steps", []) + [reasoning_step]
        }
        
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        # Fallback to escalation on failure
        return {
            "intent": "complaint",
            "confidence": 0.0,
            "escalated": True,
            "escalation_reason": f"Classification error: {str(e)}",
            "reasoning_steps": state.get("reasoning_steps", []) + ["Classification failed, escalating."]
        }
