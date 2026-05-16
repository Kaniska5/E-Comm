"""
LangSmith configuration validator - Phase 7.
"""
import os
import logging
from backend.config.settings import settings

logger = logging.getLogger(__name__)

def verify_tracing_config():
    """
    Checks if LangSmith tracing is active.
    Maps LANGSMITH_* variables to LANGCHAIN_* automatically if the user used the newer naming.
    """
    is_tracing_enabled = (
        str(os.environ.get("LANGCHAIN_TRACING_V2", "")).lower() == "true" or
        str(os.environ.get("LANGSMITH_TRACING", "")).lower() == "true"
    )

    if is_tracing_enabled:
        api_key = os.environ.get("LANGCHAIN_API_KEY") or os.environ.get("LANGSMITH_API_KEY")
        
        if not api_key:
            logger.warning("Tracing is enabled, but API key is missing! Traces will fail.")
        else:
            # Normalize environment variables for LangChain's internal use
            if not os.environ.get("LANGCHAIN_TRACING_V2"):
                os.environ["LANGCHAIN_TRACING_V2"] = "true"
            if not os.environ.get("LANGCHAIN_API_KEY") and os.environ.get("LANGSMITH_API_KEY"):
                os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGSMITH_API_KEY")
            if not os.environ.get("LANGCHAIN_PROJECT") and os.environ.get("LANGSMITH_PROJECT"):
                os.environ["LANGCHAIN_PROJECT"] = os.environ.get("LANGSMITH_PROJECT")
            if not os.environ.get("LANGCHAIN_ENDPOINT") and os.environ.get("LANGSMITH_ENDPOINT"):
                os.environ["LANGCHAIN_ENDPOINT"] = os.environ.get("LANGSMITH_ENDPOINT")
                
            logger.info("LangSmith tracing is ENABLED.")
    else:
        logger.info("LangSmith tracing is disabled.")
