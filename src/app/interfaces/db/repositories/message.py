from abc import abstractmethod
from collections.abc import Sequence

from app.db.models import MessageModel
from app.schemas import (
    MessageCreateSchema,
    MessageFetchSchema,
    MessageIDSchema,
)

from .base import AbstractGenericRepository


class AbstractMessageRepository(
    AbstractGenericRepository[MessageModel, MessageIDSchema, MessageCreateSchema]
):
    @abstractmethod
    async def fetch_messages(
        self, *, message_fetch_schema: MessageFetchSchema
    ) -> Sequence[MessageModel]: ...
