from abc import ABC, abstractmethod
from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from app.interfaces.db.repositories import (
    AbstractAttachmentRepository,
    AbstractChatRepository,
    AbstractChatUserRepository,
    AbstractMessageRepository,
    AbstractUserRepository,
)
from app.utils.types import Factory


class AbstractAsyncUnitOfWorkInContext(ABC):
    userRepository: AbstractUserRepository
    messageRepository: AbstractMessageRepository
    chatRepository: AbstractChatRepository
    chatUserRepository: AbstractChatUserRepository
    attachmentRepository: AbstractAttachmentRepository

    @abstractmethod
    def __init__(self, async_session: AsyncSession) -> None: ...


class AbstractAsyncUnitOfWork(ABC):
    _async_session: AsyncSession
    _async_session_factory: Factory[AsyncSession]

    def __init__(self, async_session_factory: Factory[AsyncSession]) -> None:
        self._async_session_factory = async_session_factory

    @abstractmethod
    async def __aenter__(self) -> AbstractAsyncUnitOfWorkInContext: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None: ...
