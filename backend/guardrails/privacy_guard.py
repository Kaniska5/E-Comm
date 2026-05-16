"""
Privacy Guardrail — Phase 5.
"""
from backend.graph.state import AgentState

def verify_privacy(state: AgentState) -> list[str]:
    """
    Ensure no cross-session data leakage.
    Validates that PII like payment details are redacted if present.
    (Simple placeholder implementation)
    """
    violations = []
    
    # In a real app, use Regex or a fast NLP model to check for credit cards, SSNs, etc.
    # Here we just ensure session isolation is maintained by confirming session_id exists.
    if not state.get("session_id"):
        violations.append("Privacy violation: missing session_id context isolation.")
        
    query = state.get("query", "").lower()
    
    # Simple dummy check for card numbers (16 digits)
    import re
    if re.search(r'\b\d{16}\b', query):
        violations.append("Privacy violation: Potential credit card number detected in query. Masking required.")
        
    return violations
