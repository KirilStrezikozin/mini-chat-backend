from fastapi import APIRouter

from . import attachments, auth, chats, health, messages, user

__all__ = [
    "api_v1_router",
]

api_v1_router = APIRouter()

api_v1_router.include_router(health.unprotected_router)

api_v1_router.include_router(attachments.protected_router)

api_v1_router.include_router(auth.protected_router)
api_v1_router.include_router(auth.unprotected_router)

api_v1_router.include_router(user.protected_router)

api_v1_router.include_router(messages.protected_router)

api_v1_router.include_router(chats.protected_router)
