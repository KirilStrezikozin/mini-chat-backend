from app.utils.router import APIRouterWithRouteProtection

from .auth import auth_router
from .chat import chats_router
from .health import health_router

__all__ = [
    "api_v1_router",
]

api_v1_router = APIRouterWithRouteProtection()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(health_router)
api_v1_router.include_router(chats_router)
