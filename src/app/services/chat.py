from sqlalchemy.orm import selectinload

from app.core.exceptions import ChatNotFoundError
from app.db.repositories import ChatRepository
from app.schemas import (
    ChatIDSchema,
    ChatInfoSchema,
    ChatRetrieveSchema,
    ChatSchema,
    ChatUserSchema,
    MessageCreateSchema,
    MessageFetchSchema,
    MessageReadSchema,
    UserIDSchema,
)

from .base import BaseService


class ChatService(BaseService):
    async def get_chats_info(
        self, *, user_schema: UserIDSchema
    ) -> list[ChatInfoSchema]:
        async with self.uow as uow:
            resources = await uow.chatUserRepository.get_chats_info(user_schema)
            return [ChatInfoSchema.model_validate(resource) for resource in resources]

    async def get_users(self, *, chat_schema: ChatIDSchema) -> list[UserIDSchema]:
        async with self.uow as uow:
            resource = await self._get_chat_resource(
                uow, chat_schema, options=[selectinload(ChatRepository.model_cls.users)]
            )
            return [UserIDSchema(id=user_model.id) for user_model in resource.users]

    async def get_or_create(
        self, *, user_schema: UserIDSchema, retrieve_schema: ChatRetrieveSchema
    ) -> ChatSchema:
        if user_schema.id == retrieve_schema.with_user_id:
            raise ChatNotFoundError

        async with self.uow as uow:
            chat_user_resource = await uow.chatUserRepository.get_chat(
                user_schema, retrieve_schema
            )

            if chat_user_resource:
                chat_user = ChatUserSchema.model_validate(chat_user_resource)
                return ChatSchema(id=chat_user.chat_id)

            user_resource = await self._get_user_resource(
                uow, UserIDSchema(id=user_schema.id)
            )

            user_with_resource = await self._get_user_resource(
                uow, UserIDSchema(id=retrieve_schema.with_user_id)
            )

            chat_resource = await uow.chatRepository.add_one()
            chat_resource.users.append(user_resource)
            chat_resource.users.append(user_with_resource)

            return ChatSchema.model_validate(chat_resource)

    async def leave(
        self, *, user_schema: UserIDSchema, chat_schema: ChatIDSchema
    ) -> None:
        async with self.uow as uow:
            user_resource = await self._get_user_resource(uow, user_schema)

            chat_resource = await self._get_chat_resource(
                uow,
                chat_schema,
                options=[
                    selectinload(ChatRepository.model_cls.users),
                    selectinload(ChatRepository.model_cls.messages),
                ],
            )

            if user_resource not in chat_resource.users:
                raise ChatNotFoundError

            chat_resource.users.clear()
            await uow.chatRepository.delete_one(chat_schema)

    async def send_message(
        self, *, user_schema: UserIDSchema, message_schema: MessageCreateSchema
    ) -> MessageReadSchema:
        async with self.uow as uow:
            # Ensure the requested chat and user exist.
            _ = await self._get_chat_resource(
                uow, ChatIDSchema(id=message_schema.chat_id)
            )
            _ = await self._get_user_resource(uow, user_schema)

            message_resource = await uow.messageRepository.add_one(message_schema)
            return MessageReadSchema.model_validate(message_resource)

    async def get_messages(
        self, *, message_fetch_schema: MessageFetchSchema
    ) -> list[MessageReadSchema]:
        async with self.uow as uow:
            # Ensure the requested chat exists.
            _ = await self._get_chat_resource(
                uow, ChatIDSchema(id=message_fetch_schema.chat_id)
            )

            resources = await uow.messageRepository.fetch_messages(
                message_fetch_schema=message_fetch_schema
            )

            return [MessageReadSchema.model_validate(v) for v in resources]
