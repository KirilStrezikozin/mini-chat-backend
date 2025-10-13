from app.utils.router import APIRouterWithRouteProtection

from .auth import auth_router
from .chat import chat_router
from .health import health_router
from .message import message_router
from .user import user_router

__all__ = [
    "api_v1_router",
]

api_v1_router = APIRouterWithRouteProtection()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(health_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(message_router)
api_v1_router.include_router(user_router)
