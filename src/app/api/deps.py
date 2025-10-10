from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import config
from app.db.session import async_session_factory
from app.utils.uow import AsyncUnitOfWork


def get_uow():
    engine = create_async_engine(config.database.uri, expire_on_commit=False)
    return AsyncUnitOfWork(async_session_factory=async_session_factory(engine))
