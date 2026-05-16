"""
LangGraph Agent State definition.
Single TypedDict used across all graph nodes.
Defined here to avoid circular imports.
"""
from typing import TypedDict, Any


class AgentState(TypedDict, total=False):
    """
    Shared state object passed between all LangGraph nodes.
    Every field is optional (total=False) so nodes can update incrementally.
    """
    # ── Session context ───────────────────────────────────────────────────────
    session_id: str          # Unique per-request ID (UUID)
    customer_id: str | None  # Resolved from query or auth

    # ── Input ─────────────────────────────────────────────────────────────────
    query: str               # Raw customer message
    chat_history: list[dict] # Prior turns in this session

    # ── Orchestrator outputs ───────────────────────────────────────────────────
    intent: str              # Classified intent (e.g. "order_tracking")
    confidence: float        # Classification confidence 0.0–1.0
    selected_agent: str      # Which agent was routed to

    # ── Retry / loop prevention ────────────────────────────────────────────────
    retry_count: int         # How many times we've retried
    max_retries: int         # Limit (from settings)

    # ── Escalation ────────────────────────────────────────────────────────────
    escalated: bool
    escalation_reason: str | None

    # ── Agent outputs ─────────────────────────────────────────────────────────
    agent_outputs: dict[str, Any]   # Keyed by agent name
    tool_calls: list[dict]          # All tool invocations this turn

    # ── Guardrails ────────────────────────────────────────────────────────────
    guardrail_violations: list[str]
    requires_human_approval: bool
    approval_id: str | None

    # ── Response ──────────────────────────────────────────────────────────────
    final_response: str

    # ── Observability ─────────────────────────────────────────────────────────
    reasoning_steps: list[str]   # Human-readable trace of decisions
    latency_ms: float | None
    error: str | None
