from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime

from app.db.models import MessageModel
from app.schemas import (
    ChatIDSchema,
    MessageCreateSchema,
    MessageIDSchema,
)

from . import AbstractGenericRepository


class AbstractMessageRepository(
    AbstractGenericRepository[MessageModel, MessageIDSchema, MessageCreateSchema]
):
    @abstractmethod
    async def fetch_messages(
        self,
        *,
        chat_id_schema: ChatIDSchema,
        since: datetime | None = None,
        until: datetime | None = None,
        count: int | None = None,
    ) -> Sequence[MessageModel]: ...
