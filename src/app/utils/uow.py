from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import (
    AttachmentRepository,
    ChatRepository,
    ChatUserRepository,
    MessageRepository,
    UserRepository,
)
from app.interfaces.utils.uow import (
    AbstractAsyncUnitOfWork,
    AbstractAsyncUnitOfWorkInContext,
)


class AsyncUnitOfWorkInContext(AbstractAsyncUnitOfWorkInContext):
    def __init__(self, async_session: AsyncSession) -> None:
        self.userRepository = UserRepository(async_session)
        self.messageRepository = MessageRepository(async_session)
        self.chatRepository = ChatRepository(async_session)
        self.chatUserRepository = ChatUserRepository(async_session)
        self.attachmentRepository = AttachmentRepository(async_session)


class AsyncUnitOfWork(AbstractAsyncUnitOfWork):
    async def __aenter__(self) -> AsyncUnitOfWorkInContext:
        self._async_session = self._async_session_factory()
        return AsyncUnitOfWorkInContext(self._async_session)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None:
        _ = exc_type, tb
        assert self._async_session is not None

        try:
            if exc:
                await self._async_session.rollback()
            else:
                await self._async_session.commit()
        finally:
            await self._async_session.close()
