from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

health_router = APIRouter(tags=["health"])


@health_router.get("/health")
async def health(request: Request) -> None:
    db_engine: AsyncEngine = request.app.state.engine
    try:
        async with db_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as error:
        raise HTTPException(status_code=503, detail="Database is down") from error
