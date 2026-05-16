"""
API Router assembly.
"""
from fastapi import APIRouter

from backend.api.routes import chat, orders, refunds, approvals, logs

api_router = APIRouter()

api_router.include_router(chat.router)
api_router.include_router(orders.router)
api_router.include_router(refunds.router)
api_router.include_router(approvals.router)
api_router.include_router(logs.router)
