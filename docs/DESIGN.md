# System Design Document
# Agentic AI Customer Support System

## 1. Problem Statement

A large e-commerce company receives 10,000+ customer queries daily with a 6-hour average response time and declining CSAT scores. This system replaces the manual support queue with an AI-powered agent pipeline that resolves 80%+ of queries instantly.

---

## 2. Architecture Overview

```
Customer
   |
   v
[Streamlit UI] ─── HTTP ──→ [FastAPI Backend]
                                    |
                                    v
                        [LangGraph Orchestrator]
                                    |
                       Intent Classification Node
                                    |
                    ┌───────────────┼───────────────┐
                    v               v               v       v
            [Order Agent]  [Refund Agent]  [FAQ Agent]  [Escalation]
                    |               |               |
                    └───────────────┴───────────────┘
                                    |
                          [Guardrails Layer]
                                    |
                     ┌──────────────┴──────────────┐
                     v                              v
             [Auto Execute]              [Human Approval Queue]
                     |                              |
                     └──────────────┬──────────────┘
                                    v
                          [Response Synthesizer]
                                    |
                     ┌──────────────┴──────────────┐
                     v                              v
              [SQLite Audit Log]          [LangSmith Trace]
```

---

## 3. LangGraph Workflow

### State Object (`AgentState`)

```python
class AgentState(TypedDict):
    session_id: str
    query: str
    intent: str
    confidence: float
    retry_count: int
    escalated: bool
    agent_outputs: dict
    guardrail_violations: list
    tool_calls: list
    final_response: str
    requires_human_approval: bool
    approval_id: str | None
```

### Graph Nodes

| Node | Type | Role |
|---|---|---|
| `intent_classifier` | LLM | Classifies query intent + confidence score |
| `order_agent` | LLM + Tools | Order lookup, shipment tracking |
| `refund_agent` | LLM + Tools + Guardrail | Refund eligibility + threshold check |
| `faq_agent` | Retrieval | Keyword match against `policies.md` |
| `escalation_agent` | Workflow | Queues ticket, notifies human |
| `synthesizer` | LLM | Formats final customer-facing response |

### Routing Logic

```
intent_classifier
    ├── "order_tracking"  → order_agent
    ├── "refund_request"  → refund_agent
    ├── "faq"             → faq_agent
    ├── "complaint"       → escalation_agent
    ├── confidence < 0.4  → escalation_agent
    └── retry_count >= 2  → escalation_agent (forced)
```

---

## 4. Guardrails

### A. Refund Limit Guard

- Refund amount extracted from agent output
- If amount <= Rs 1000 → `auto_approve`
- If amount > Rs 1000 → `pending_approval`, create `human_approvals` record
- **No bypass possible** — check runs before any DB write

### B. Privacy Guard

- Sessions are isolated via `session_id`
- No cross-session memory — LangGraph state is ephemeral per request
- PII fields (payment info, address) are never included in LLM prompts

### C. Loop Guard

- `retry_count` tracked in `AgentState`
- `max_retries = 2` (configurable via `MAX_AGENT_RETRIES` env var)
- On `retry_count >= max_retries` → forced escalation

### D. Tool Access Control

| Agent | Allowed Tools |
|---|---|
| order_agent | `lookup_order`, `track_shipment` |
| refund_agent | `check_refund_eligibility`, `process_refund` |
| faq_agent | `search_faq` (local file only) |
| escalation_agent | `create_ticket`, `notify_human` |

---

## 5. Human-in-the-Loop (HITL) Workflow

```
High-risk action detected
         |
         v
Guardrail → blocks execution
         |
         v
Creates `human_approvals` record (status=pending)
         |
         v
Returns holding response to customer
         |
         v
Human reviews in Streamlit Approval Dashboard
         |
    ┌────┴────┐
    v         v
Approve     Reject
    |         |
    v         v
Execute    Decline + notify customer
```

### Triggers

1. Refund > Rs 1000
2. Fraud suspicion flag from agent
3. Legal complaint keyword detected
4. Customer frustration score > threshold
5. Retry limit exceeded

---

## 6. Database Design

### Tables

```sql
customers      -- customer profiles
orders         -- order records with status
refunds        -- refund requests + approval status
faq_documents  -- indexed FAQ sections
escalation_tickets -- support ticket queue
human_approvals    -- HITL approval queue
audit_logs         -- every event in the system
```

---

## 7. Monitoring & Observability

### Dual-layer logging

1. **SQLite `audit_logs`** — every event persisted locally (no external dependency)
2. **LangSmith** — full trace of every LangGraph run (optional, key-gated)

### What is logged

| Event | Where |
|---|---|
| Incoming query | audit_logs + LangSmith |
| Intent classification | audit_logs + LangSmith |
| Agent selected | audit_logs |
| Tool calls | audit_logs + LangSmith |
| Guardrail check | audit_logs |
| Guardrail violation | audit_logs (WARN) |
| Escalation trigger | audit_logs |
| Human approval | audit_logs |
| Final response | audit_logs + LangSmith |
| Latency (ms) | audit_logs + LangSmith |

---

## 8. Architecture Decisions & Tradeoffs

| Decision | Rationale |
|---|---|
| SQLite over PostgreSQL | Zero infra overhead; sufficient for 10K queries/day in local-first setup |
| Streamlit over React | No build tooling; Python-native; faster iteration for AI apps |
| uv over pip/poetry | Significantly faster; lockfile-based; modern standard |
| Simple keyword FAQ | Avoids vector DB complexity; sufficient for structured policy docs |
| Single orchestrator | Prevents conflicting routing decisions; easier to debug and audit |
| Synchronous HITL | Explicit, auditable; avoids async approval race conditions |

---

## 9. Future Improvements

- [ ] Swap SQLite for PostgreSQL for multi-node deployments
- [ ] Add vector embeddings for FAQ if document count exceeds 100
- [ ] Stream LLM responses via Server-Sent Events
- [ ] Webhook notifications for human approvers
- [ ] Rate limiting per session
- [ ] A/B testing for different LLM models
- [ ] Load testing with Locust
