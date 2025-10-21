from collections.abc import Sequence
from typing import Any

from sqlalchemy.orm.interfaces import ORMOption

from app.core.config import Config
from app.core.exceptions import (
    ChatNotFoundError,
    MessageNotFoundError,
    UserNotFoundError,
)
from app.db.models import ChatModel, MessageModel, UserModel
from app.interfaces.db.repositories import AbstractGenericRepository
from app.interfaces.utils.uow import (
    AbstractAsyncUnitOfWork,
    AbstractAsyncUnitOfWorkInContext,
)
from app.schemas import ChatIDSchema, IDSchema, MessageIDSchema, UserIDSchema


class BaseService:
    def __init__(self, config: Config, uow: AbstractAsyncUnitOfWork) -> None:
        self.config = config
        self.uow = uow

    async def _get_resource(
        self,
        *,
        repo: AbstractGenericRepository,
        schema: IDSchema,
        options: Sequence[ORMOption] | None = None,
        exc: type[Exception],
    ) -> Any:
        resource = await repo.get(schema, options)
        if not resource:
            raise exc
        return resource

    async def _get_user_resource(
        self,
        uow: AbstractAsyncUnitOfWorkInContext,
        user_schema: UserIDSchema,
        options: Sequence[ORMOption] | None = None,
    ) -> UserModel:
        return await self._get_resource(
            repo=uow.userRepository,
            schema=user_schema,
            options=options,
            exc=UserNotFoundError,
        )

    async def _get_message_resource(
        self,
        uow: AbstractAsyncUnitOfWorkInContext,
        message_schema: MessageIDSchema,
        options: Sequence[ORMOption] | None = None,
    ) -> MessageModel:
        return await self._get_resource(
            repo=uow.messageRepository,
            schema=message_schema,
            options=options,
            exc=MessageNotFoundError,
        )

    async def _get_chat_resource(
        self,
        uow: AbstractAsyncUnitOfWorkInContext,
        chat_schema: ChatIDSchema,
        options: Sequence[ORMOption] | None = None,
    ) -> ChatModel:
        return await self._get_resource(
            repo=uow.chatRepository,
            schema=chat_schema,
            options=options,
            exc=ChatNotFoundError,
        )
