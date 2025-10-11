from fastapi import APIRouter

from .auth import auth_router

__all__ = [
    "api_v1_router",
]

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
