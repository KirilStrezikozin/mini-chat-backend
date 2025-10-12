from collections.abc import Sequence
from typing import override

from sqlalchemy import Row, select
from sqlalchemy.orm import aliased

from app.db.models import ChatModel, ChatUserModel, PrimaryKeyID, UserModel
from app.db.repositories import GenericRepository
from app.interfaces.db.repositories import (
    AbstractChatRepository,
    AbstractChatUserRepository,
)
from app.schemas import ChatIDSchema, ChatRetrieveSchema, ChatSchema, UserIDSchema
from app.utils.types import IDType


class ChatRepository(
    AbstractChatRepository,
    GenericRepository[ChatModel, ChatIDSchema, ChatSchema],
    model=ChatModel,
):
    @override
    async def add_one(self, entity: ChatSchema | None = None) -> ChatModel:
        _ = entity
        obj = self.model_cls()
        self._session.add(obj)
        return obj


class ChatUserRepository(
    AbstractChatUserRepository,
):
    model_cls = ChatUserModel

    async def get_chats_info(
        self, idSchema: UserIDSchema
    ) -> Sequence[Row[tuple[IDType, PrimaryKeyID, str, str]]]:
        cu1 = aliased(self.model_cls)
        cu2 = aliased(self.model_cls)
        u2 = aliased(UserModel)

        stmt = (
            select(cu1.chat_id, u2.id, u2.fullname, u2.username)
            .join(cu2, cu1.chat_id == cu2.chat_id)
            .join(u2, u2.id == cu2.user_id)
            .where(
                cu1.user_id == idSchema.id,
                cu2.user_id != idSchema.id,
            )
        )

        result = await self._session.execute(stmt)
        return result.all()

    async def get_chat(
        self, userIdSchema: UserIDSchema, retrieveSchema: ChatRetrieveSchema
    ) -> ChatUserModel | None:
        cu1 = aliased(self.model_cls)
        cu2 = aliased(self.model_cls)

        shared_chat_stmt = (
            select(cu1)
            .join(cu2, cu1.chat_id == cu2.chat_id)
            .where(
                cu1.user_id == userIdSchema.id,
                cu2.user_id == retrieveSchema.with_user_id,
            )
        )

        result = await self._session.scalar(shared_chat_stmt)
        return result
