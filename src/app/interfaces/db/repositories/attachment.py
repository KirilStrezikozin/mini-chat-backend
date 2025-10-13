from abc import abstractmethod
from collections.abc import Sequence

from app.db.models import AttachmentModel
from app.schemas import (
    AttachmentCreateSchema,
    AttachmentIDSchema,
    ChatIDSchema,
)

from .base import AbstractGenericRepository


class AbstractAttachmentRepository(
    AbstractGenericRepository[
        AttachmentModel, AttachmentIDSchema, AttachmentCreateSchema
    ],
):
    @abstractmethod
    async def get_all_in_chat(
        self, chat_schema: ChatIDSchema
    ) -> Sequence[AttachmentModel]: ...
