from app.schemas import (
    MessageEditSchema,
    MessageIDSchema,
    MessageReadSchema,
)

from . import BaseService
from .exceptions import MessageNotFoundError


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
