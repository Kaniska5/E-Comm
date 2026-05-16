# Design Thinking Approach: Agentic AI Support System

Welcome to the design documentation for the **Agentic E-Commerce Customer Support System**. This document outlines the user-centered **Design Thinking** methodology we applied to architect, build, and refine this platform. 

Design Thinking is a non-linear, iterative process that teams use to understand users, challenge assumptions, redefine problems, and create innovative solutions. Our approach is broken down into five core phases: **Empathize, Define, Ideate, Prototype, and Test**.

---

## 1. Empathize: Understanding the User
The first step in our process was to deeply understand the pain points of our two primary stakeholders: the **Customers** and the **Customer Support Agents**.

### The Customer's Pain Points:
- **Long Wait Times:** Customers are waiting up to 6 hours for simple queries like "Where is my order?" or "Can I get a refund?"
- **Inconsistent Answers:** Different human agents provide slightly different policy interpretations.
- **Frustration with "Dumb" Bots:** Existing chatbots only offer pre-written decision trees and cannot actually execute backend actions (like processing refunds).

### The Support Agent's Pain Points:
- **Burnout:** Agents spend 80% of their day answering repetitive, easily solvable queries.
- **Cognitive Load:** High-stress situations involving angry customers demanding immediate escalations.
- **Compliance Risks:** Accidentally approving refunds that violate the 10-day limit or exceed maximum monetary thresholds.

---

## 2. Define: Stating Your Users' Needs and Problems
After analyzing our empathy findings, we defined the core problem statement:

> *"How might we empower customers to instantly resolve routine queries (tracking, refunds, FAQs) securely and autonomously, while reserving human support agents strictly for high-value or emotionally sensitive escalations?"*

### Key Requirements Defined:
- **Autonomy with Safety:** The AI must take action (e.g., issue refunds) but never exceed a strict limit (₹1000).
- **Specialization:** The AI cannot hallucinate policies. It needs specialized knowledge for different tasks.
- **Graceful Handoff:** If the AI is confused, or the customer is angry, it must instantly escalate to a human.

---

## 3. Ideate: Challenging Assumptions and Creating Ideas
During the ideation phase, we brainstormed architectural solutions to meet the defined requirements. 

**Idea 1: A single massive LLM (Rejected)**
- *Why:* Prompting one model to handle orders, refunds, and FAQs simultaneously leads to hallucinations and massive security risks. A single prompt could be easily bypassed via prompt injection to grant unauthorized refunds.

**Idea 2: Agentic Workflow Orchestration (Selected)**
- *Why:* We decided to use a **LangGraph Orchestrator** pattern. 
- A "Brain" (Orchestrator) simply reads the user intent and routes it to an isolated, specialized "Sub-Agent".
- The **Order Agent** only has database tools for tracking. It cannot issue refunds.
- The **Refund Agent** has refund tools, but these tools are protected by hardcoded Python Guardrails that cannot be manipulated by the LLM.

---

## 4. Prototype: Start to Create Solutions
We built the system incrementally, breaking it down into manageable phases.

### Phase 1 & 2: The Foundation
- We set up a local-first **FastAPI** backend and an asynchronous **SQLite** database.
- We created the tables (`Orders`, `Refunds`, `HumanApprovals`) to simulate a real e-commerce backend.

### Phase 3: The Brain (Orchestrator)
- We built the **Intent Classifier** using Google's `gemma-4-26b-a4b-it` model. We strictly typed its output so it could only ever route to our specific agents.

### Phase 4 & 5: The Specialized Agents & Guardrails
- We built the **Least-Privilege Agents**. 
- We built the **Refund Guardrail**: If the AI attempts to refund > ₹1000, a Python script intercepts the request, blocks it, and generates a ticket. 

### Phase 6 & 8: The Human-in-the-Loop (HITL) UI
- We built a **Streamlit Dashboard** featuring a Chat UI for the customer and an Approval Dashboard for the human support team to review the intercepted high-value refunds.

---

## 5. Test: Try Your Solutions Out
The testing phase is continuous. We implemented robust verification to ensure the system behaves safely.

### Automated Testing (Pytest)
- We wrote unit tests simulating malicious or high-value requests. 
- *Result:* The tests proved that the Guardrail successfully intercepts ₹1500 refund requests and flags them for human review, preventing financial loss.

### Observability (LangSmith & SQLite)
- We implemented an **Audit Logger**. Every single decision the AI makes is permanently logged into the database.
- We integrated **LangSmith** to visualize the AI's internal thought process step-by-step. If an AI hallucinates, we can see exactly which prompt caused it and refine our system.

---

## Conclusion
By applying Design Thinking, we transformed a frustrating, slow customer support pipeline into a **rapid, autonomous, and incredibly safe** Agentic AI system. Customers get instant, actionable support, and human agents are freed to focus on complex, high-value tasks via the Approval Dashboard.
