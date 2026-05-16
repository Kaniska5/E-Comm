"""
Refund Guardrail — Phase 5.
"""
from backend.config.settings import settings

def validate_refund_amount(amount: float) -> bool:
    """
    Check if a refund amount can be auto-approved.
    Returns True if auto-approved, False if human approval is required.
    """
    if amount <= settings.REFUND_AUTO_APPROVE_LIMIT:
        return True
    return False
