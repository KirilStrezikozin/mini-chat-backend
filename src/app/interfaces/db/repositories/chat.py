from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import override

from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatModel, ChatUserModel
from app.db.models.mappings import PrimaryKeyID
from app.schemas import ChatIDSchema, ChatRetrieveSchema, ChatSchema, UserIDSchema
from app.utils.types import IDType

from .base import AbstractGenericRepository


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
    async def get_chats_info(
        self, idSchema: UserIDSchema
    ) -> Sequence[Row[tuple[IDType, PrimaryKeyID, str, str]]]: ...

    @abstractmethod
    async def get_chat(
        self, userIdSchema: UserIDSchema, retrieveSchema: ChatRetrieveSchema
    ) -> ChatUserModel | None: ...
