from abc import ABC, abstractmethod
from typing import override

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatModel, ChatUserModel
from app.schemas import ChatIDSchema, ChatRetrieveSchema, ChatSchema

from . import AbstractGenericRepository


class AbstractChatRepository(
    AbstractGenericRepository[ChatModel, ChatIDSchema, ChatSchema]
):
    @override
    @abstractmethod
    async def add_one(self, entity: ChatSchema | None = None) -> ChatModel: ...


class AbstractChatUserRepository(ABC):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    async def get_chat(
        self, retrieveSchema: ChatRetrieveSchema
    ) -> ChatUserModel | None: ...
