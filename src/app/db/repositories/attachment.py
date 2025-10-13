from collections.abc import Sequence

from sqlalchemy import select

from app.db.models import AttachmentModel, MessageModel
from app.interfaces.db.repositories import AbstractAttachmentRepository
from app.schemas import AttachmentCreateSchema, AttachmentIDSchema, ChatIDSchema

from .base import GenericRepository


class AttachmentRepository(
    AbstractAttachmentRepository,
    GenericRepository[AttachmentModel, AttachmentIDSchema, AttachmentCreateSchema],
    model=AttachmentModel,
):
    async def get_all_in_chat(
        self, chat_schema: ChatIDSchema
    ) -> Sequence[AttachmentModel]:
        stmt = (
            select(self.model_cls)
            .join(self.model_cls.message)
            .where(MessageModel.chat_id == chat_schema.id)
        )

        res = await self._session.execute(stmt)
        return res.scalars().all()
