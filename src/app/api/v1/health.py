from fastapi import APIRouter

unprotected_router = APIRouter(tags=["health"])


@unprotected_router.get("/health")
async def health() -> str:
    return "healthy"
