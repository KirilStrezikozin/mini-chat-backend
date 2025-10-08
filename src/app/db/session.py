from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Config


@asynccontextmanager
async def get_async_engine(
    config: Config,
    **create_async_engine_kw: Any,
) -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(config.database.uri, **create_async_engine_kw)
    try:
        yield engine
    finally:
        await engine.dispose()


def async_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)
