"""
Tools for the FAQ Agent.
"""
import os
from langchain_core.tools import tool

FAQ_PATH = os.path.join(os.path.dirname(__file__), "../../data/faq/policies.md")

@tool
async def search_faq(query: str) -> str:
    """Search the company policies and FAQ for answers to generic questions."""
    try:
        with open(FAQ_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            
        # In a real app with huge docs, we'd chunk and keyword match.
        # Here we just return the full text for the LLM to extract the answer from,
        # as it's a "lightweight RAG" for a small doc.
        return content
    except FileNotFoundError:
        return "FAQ document not found."
