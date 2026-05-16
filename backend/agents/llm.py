"""
LLM Factory — instantiates the configured LLM based on environment settings.
"""
from langchain_core.language_models.chat_models import BaseChatModel
from backend.config.settings import settings

def get_llm(temperature: float = 0.0) -> BaseChatModel:
    """Get the configured LLM instance."""
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=temperature
        )
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=temperature
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
