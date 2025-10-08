from typing import override

from sqlalchemy import select

from app.db.models import ChatModel, ChatUserModel
from app.db.repositories import GenericRepository
from app.interfaces.db.repositories import (
    AbstractChatRepository,
    AbstractChatUserRepository,
)
from app.schemas import ChatIDSchema, ChatRetrieveSchema, ChatSchema


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


class ChatUserRepository(AbstractChatUserRepository):
    model_cls = ChatUserModel

    async def get_chat(
        self, retrieveSchema: ChatRetrieveSchema
    ) -> ChatUserModel | None:
        stmt = select(self.model_cls.chat_id).where(
            self.model_cls.user_id == retrieveSchema.user_id
        )

        shared_chat_stmt = select(self.model_cls).where(
            self.model_cls.user_id == retrieveSchema.with_user_id,
            self.model_cls.chat_id.in_(stmt),
        )

        result = await self._session.scalar(shared_chat_stmt)
        return result
