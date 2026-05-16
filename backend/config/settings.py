"""
Application settings — loaded from environment variables via pydantic-settings.
All config lives here. No magic strings scattered across the codebase.
"""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Explicitly load .env into os.environ so third-party libraries (like LangChain)
# can pick up the keys natively.
load_dotenv()

# Map LANGSMITH_ to LANGCHAIN_ natively immediately at boot
if os.environ.get("LANGSMITH_TRACING") and not os.environ.get("LANGCHAIN_TRACING_V2"):
    os.environ["LANGCHAIN_TRACING_V2"] = os.environ.get("LANGSMITH_TRACING")
if os.environ.get("LANGSMITH_API_KEY") and not os.environ.get("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGSMITH_API_KEY")
if os.environ.get("LANGSMITH_PROJECT") and not os.environ.get("LANGCHAIN_PROJECT"):
    os.environ["LANGCHAIN_PROJECT"] = os.environ.get("LANGSMITH_PROJECT")
if os.environ.get("LANGSMITH_ENDPOINT") and not os.environ.get("LANGCHAIN_ENDPOINT"):
    os.environ["LANGCHAIN_ENDPOINT"] = os.environ.get("LANGSMITH_ENDPOINT")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "Agentic AI Support"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # ── API ──────────────────────────────────────────────────────────────────
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_URL: str = "http://localhost:8000"
    ALLOWED_ORIGINS: str = "http://localhost:8501,http://localhost:3000"

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./support_ai.db"

    # ── LLM ──────────────────────────────────────────────────────────────────
    # Provider: "gemini" | "openai"
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemma-4-26b-a4b-it"

    GOOGLE_API_KEY: str = Field(default="", alias="GOOGLE_API_KEY")
    OPENAI_API_KEY: str = Field(default="", alias="OPENAI_API_KEY")

    # ── LangSmith ────────────────────────────────────────────────────────────
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "agentic-support-ai"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

    # ── Guardrails ───────────────────────────────────────────────────────────
    # Refunds above this amount require human approval (in ₹)
    REFUND_AUTO_APPROVE_LIMIT: float = 1000.0
    MAX_AGENT_RETRIES: int = 2

    # ── Computed helpers ──────────────────────────────────────────────────────
    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


# Singleton — import this everywhere
settings = Settings()
