"""API routes."""

from fastapi import APIRouter

from backend.app.api import (
    agent_templates,
    agents,
    analytics,
    auth,
    chat,
    group_chat,
    logs,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(
    agent_templates.router, prefix="/agent-templates", tags=["agent-templates"]
)
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(
    group_chat.router, prefix="/group-chats", tags=["group-chats"]
)
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
