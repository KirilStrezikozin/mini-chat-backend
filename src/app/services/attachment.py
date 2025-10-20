from app.core.exceptions import AttachmentNotFoundError, ChatNotFoundError
from app.schemas import AttachmentIDSchema, AttachmentReadSchema, ChatIDSchema

from .base import BaseService


class AttachmentService(BaseService):
    async def get(
        self, *, attachment_schema: AttachmentIDSchema
    ) -> AttachmentReadSchema:
        async with self.uow as uow:
            resource = await uow.attachmentRepository.get(attachment_schema)
            if not resource:
                raise AttachmentNotFoundError
            return AttachmentReadSchema.model_validate(resource)

    async def get_all_in_chat(
        self, *, chat_schema: ChatIDSchema
    ) -> list[AttachmentReadSchema]:
        async with self.uow as uow:
            if not await uow.chatRepository.get(chat_schema):
                raise ChatNotFoundError

            resources = await uow.attachmentRepository.get_all_in_chat(
                chat_schema=chat_schema
            )

            return [AttachmentReadSchema.model_validate(v) for v in resources]
