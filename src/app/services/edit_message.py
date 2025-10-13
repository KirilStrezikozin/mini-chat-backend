from app.schemas import (
    MessageEditSchema,
    MessageIDSchema,
)

from . import BaseService
from .exceptions import MessageNotFoundError


class EditMessageService(BaseService):
    async def edit(self, *, editSchema: MessageEditSchema) -> None:
        async with self.uow as uow:
            idSchema = MessageIDSchema(id=editSchema.id)
            message = await uow.messageRepository.get(idSchema)
            if not message:
                raise MessageNotFoundError
            await uow.messageRepository.update_one(idSchema, content=editSchema.content)
            await uow.commit()

    async def delete(self, *, idSchema: MessageIDSchema) -> None:
        async with self.uow as uow:
            message = await uow.messageRepository.get(idSchema)
            if not message:
                raise MessageNotFoundError
            await uow.messageRepository.delete_one(idSchema)
            await uow.commit()
