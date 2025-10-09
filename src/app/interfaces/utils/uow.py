from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.interfaces.db.repositories import (
    AbstractChatRepository,
    AbstractChatUserRepository,
    AbstractMessageRepository,
    AbstractUserRepository,
)
from app.utils.types import Factory


class AbstractAsyncUnitOfWork(ABC):
    _async_session: AsyncSession
    _async_session_factory: Factory[AsyncSession]

    userRepository: AbstractUserRepository
    messageRepository: AbstractMessageRepository
    chatRepository: AbstractChatRepository
    chatUserRepository: AbstractChatUserRepository

    def __init__(self, async_session_factory: Factory[AsyncSession]) -> None:
        self._async_session_factory = async_session_factory

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None: ...

    @abstractmethod
    async def commit(self) -> None: ...
