from fastapi import APIRouter

from .auth import auth_router
from .chat import chat_router
from .health import health_router

__all__ = [
    "api_v1_router",
]

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(health_router)
api_v1_router.include_router(chat_router)
