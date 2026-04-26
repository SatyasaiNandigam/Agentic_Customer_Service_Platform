
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.chat import router as chat_router
from app.api.v1.feedback import router as feedback_router



api_router = APIRouter()

api_router.include_router(health_router, prefix="/v1", tags=["health"])

# Auth — POST /auth/login, /auth/refresh, /auth/logout
api_router.include_router(auth_router, prefix="/v1", tags=["auth"])

# Chat — POST /chat, WebSocket /chat/ws, GET /chat/history/{session_id}
api_router.include_router(chat_router, prefix="/v1", tags=["chat"])

# Feedback — POST /feedback (LangSmith user satisfaction ratings)
api_router.include_router(feedback_router, prefix="/v1", tags=["feedback"])