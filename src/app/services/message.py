from sqlalchemy.orm import selectinload

from app.db.repositories import ChatRepository, MessageRepository
from app.schemas import (
    MessageEditSchema,
    MessageIDSchema,
    MessageReadSchema,
    UserReadSchema,
)

from .base import BaseService


class MessageService(BaseService):
    async def get(self, *, message_schema: MessageIDSchema) -> MessageReadSchema:
        async with self.uow as uow:
            message_resource = await self._get_message_resource(uow, message_schema)
            return MessageReadSchema.model_validate(message_resource)

    async def patch(self, *, message_schema: MessageEditSchema) -> MessageReadSchema:
        async with self.uow as uow:
            # Ensure the requested message exists.
            _ = await self._get_message_resource(uow, message_schema)
            message_resource = await uow.messageRepository.update_one(
                message_schema,
                MessageRepository.model_cls,
                content=message_schema.content,
            )
            return MessageReadSchema.model_validate(message_resource)

    async def delete(self, *, message_schema: MessageIDSchema) -> None:
        async with self.uow as uow:
            # Ensure the requested message exists.
            _ = await self._get_message_resource(uow, message_schema)
            await uow.messageRepository.delete_one(message_schema)

    async def get_users_of_chat(
        self, *, message_schema: MessageIDSchema
    ) -> list[UserReadSchema]:
        async with self.uow as uow:
            message_resource = await self._get_message_resource(
                uow,
                message_schema,
                options=[
                    selectinload(
                        MessageRepository.model_cls.chat,
                    ).selectinload(
                        ChatRepository.model_cls.users,
                    ),
                ],
            )

            return [
                UserReadSchema.model_validate(model)
                for model in message_resource.chat.users
            ]
