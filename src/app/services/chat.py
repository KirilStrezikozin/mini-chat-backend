from sqlalchemy.orm import selectinload

from app.core.exceptions import ChatNotFoundError, UserNotFoundError
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
    async def get_chats(self, *, userIDSchema: UserIDSchema) -> list[ChatSchema]:
        async with self.uow as uow:
            resource = await uow.userRepository.get(userIDSchema)
            if not resource:
                raise UserNotFoundError

            return [ChatSchema.model_validate(chat) for chat in resource.chats]

    async def get_chats_info(
        self, *, userIDSchema: UserIDSchema
    ) -> list[ChatInfoSchema]:
        async with self.uow as uow:
            resources = await uow.chatUserRepository.get_chats_info(userIDSchema)
            return [ChatInfoSchema.model_validate(resource) for resource in resources]

    async def get_users(self, *, chatIDSchema: ChatIDSchema) -> list[UserIDSchema]:
        async with self.uow as uow:
            resource = await uow.chatRepository.get(
                chatIDSchema,
                options=[selectinload(ChatRepository.model_cls.users)],
            )

            if not resource:
                raise ChatNotFoundError

            return [UserIDSchema(id=user_model.id) for user_model in resource.users]

    async def get_or_create_chat(
        self, *, userIDSchema: UserIDSchema, retrieveSchema: ChatRetrieveSchema
    ) -> ChatSchema:
        if userIDSchema.id == retrieveSchema.with_user_id:
            raise ChatNotFoundError

        async with self.uow as uow:
            chatUserResource = await uow.chatUserRepository.get_chat(
                userIDSchema, retrieveSchema
            )
            if chatUserResource:
                chatUser = ChatUserSchema.model_validate(chatUserResource)
                return ChatSchema(id=chatUser.chat_id)

            userResource = await uow.userRepository.get(
                UserIDSchema(id=userIDSchema.id)
            )
            userWithResource = await uow.userRepository.get(
                UserIDSchema(id=retrieveSchema.with_user_id)
            )

            if not userResource or not userWithResource:
                raise UserNotFoundError

            chatResource = await uow.chatRepository.add_one()
            chatResource.users.append(userResource)
            chatResource.users.append(userWithResource)
            await uow.commit()

            return ChatSchema.model_validate(chatResource)

    async def leave_chat(self, *, chatUserSchema: ChatUserSchema) -> None:
        async with self.uow as uow:
            userResource = await uow.userRepository.get(
                UserIDSchema(id=chatUserSchema.user_id)
            )
            if not userResource:
                raise UserNotFoundError

            chatResource = await uow.chatRepository.get(
                ChatIDSchema(id=chatUserSchema.chat_id),
                options=[
                    selectinload(ChatRepository.model_cls.users),
                    selectinload(ChatRepository.model_cls.messages),
                ],
            )

            if not chatResource:
                raise ChatNotFoundError

            if userResource in chatResource.users:
                chatResource.users.clear()
                chatResource.messages.clear()
            else:
                raise ChatNotFoundError

            await uow.chatRepository.delete_one(ChatIDSchema(id=chatUserSchema.chat_id))
            await uow.commit()

    async def send_message(
        self, *, messageSchema: MessageCreateSchema
    ) -> MessageReadSchema:
        async with self.uow as uow:
            chatResource = await uow.chatRepository.get(
                ChatIDSchema(id=messageSchema.chat_id),
            )
            if not chatResource:
                raise ChatNotFoundError

            userResource = await uow.userRepository.get(
                UserIDSchema(id=messageSchema.sender_id)
            )
            if not userResource:
                raise UserNotFoundError

            resource = await uow.messageRepository.add_one(messageSchema)

            await uow.commit()
            return MessageReadSchema.model_validate(resource)

    async def get_messages(
        self, *, messageFetchSchema: MessageFetchSchema
    ) -> list[MessageReadSchema]:
        async with self.uow as uow:
            chatResource = await uow.chatRepository.get(
                ChatIDSchema(id=messageFetchSchema.chat_id),
            )
            if not chatResource:
                raise ChatNotFoundError

            resource = await uow.messageRepository.fetch_messages(
                chat_id_schema=ChatIDSchema(id=messageFetchSchema.chat_id),
                since=messageFetchSchema.since,
                until=messageFetchSchema.until,
                count=messageFetchSchema.count,
            )

            return [MessageReadSchema.model_validate(model) for model in resource]
