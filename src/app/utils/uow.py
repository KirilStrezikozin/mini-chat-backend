from types import TracebackType
from typing import Self

from app.db.repositories import (
    ChatRepository,
    ChatUserRepository,
    MessageRepository,
    UserRepository,
)
from app.interfaces.utils.uow import AbstractAsyncUnitOfWork


class AsyncUnitOfWork(AbstractAsyncUnitOfWork):
    async def __aenter__(self) -> Self:
        self._async_session = self._async_session_factory()
        self.userRepository = UserRepository(self._async_session)
        self.messageRepository = MessageRepository(self._async_session)
        self.chatRepository = ChatRepository(self._async_session)
        self.chatUserRepository = ChatUserRepository(self._async_session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None:
        _ = exc_type, tb
        assert self._async_session is not None

        if exc:
            await self._async_session.rollback()
        await self._async_session.close()

    async def commit(self) -> None:
        assert self._async_session is not None
        await self._async_session.commit()
