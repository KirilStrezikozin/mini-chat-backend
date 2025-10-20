from sqlalchemy.orm import selectinload

from app.core.exceptions import MessageNotFoundError
from app.db.repositories import ChatRepository, MessageRepository
from app.schemas import (
    AttachmentCreateSchema,
    AttachmentReadSchema,
    MessageEditSchema,
    MessageIDSchema,
    MessageReadSchema,
    UserReadSchema,
)

from .base import BaseService


class MessageService(BaseService):
    async def get(self, *, message_schema: MessageIDSchema) -> MessageReadSchema:
        async with self.uow as uow:
            resource = await uow.messageRepository.get(message_schema)
            if not resource:
                raise MessageNotFoundError
            return MessageReadSchema.model_validate(resource)

    async def edit(self, *, message_schema: MessageEditSchema) -> None:
        async with self.uow as uow:
            resource = await uow.messageRepository.get(message_schema)
            if not resource:
                raise MessageNotFoundError

            await uow.messageRepository.update_one(
                message_schema, content=message_schema.content
            )

            await uow.commit()

    async def delete(self, *, message_schema: MessageIDSchema) -> None:
        async with self.uow as uow:
            resource = await uow.messageRepository.get(message_schema)
            if not resource:
                raise MessageNotFoundError

            await uow.messageRepository.delete_one(message_schema)
            await uow.commit()

    async def add_attachment(self, *, schema: AttachmentCreateSchema):
        async with self.uow as uow:
            resource = await uow.messageRepository.get(
                MessageIDSchema(id=schema.message_id),
                options=[selectinload(MessageRepository.model_cls.attachments)],
            )
            if not resource:
                raise MessageNotFoundError

            attachmentResource = await uow.attachmentRepository.add_one(schema)

            resource.attachments.append(attachmentResource)
            await uow.commit()

            attachment = AttachmentReadSchema.model_validate(attachmentResource)
            return attachment

    async def get_attachments(
        self, *, message_schema: MessageIDSchema
    ) -> list[AttachmentReadSchema]:
        async with self.uow as uow:
            resource = await uow.messageRepository.get(
                message_schema,
                options=[selectinload(MessageRepository.model_cls.attachments)],
            )
            if not resource:
                raise MessageNotFoundError

            return [
                AttachmentReadSchema.model_validate(model)
                for model in resource.attachments
            ]

    async def get_users_for_message_in_chat(
        self, *, message_schema: MessageIDSchema
    ) -> list[UserReadSchema]:
        async with self.uow as uow:
            resource = await uow.messageRepository.get(
                message_schema,
                options=[
                    selectinload(
                        MessageRepository.model_cls.chat,
                    ).selectinload(
                        ChatRepository.model_cls.users,
                    ),
                ],
            )
            if not resource:
                raise MessageNotFoundError

            return [
                UserReadSchema.model_validate(model) for model in resource.chat.users
            ]
