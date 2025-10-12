from collections.abc import Iterable

from sqlalchemy.orm import selectinload

from app.db.repositories.chat import ChatRepository
from app.schemas import (
    ChatIDSchema,
    ChatInfoSchema,
    ChatRetrieveSchema,
    ChatSchema,
    ChatUserSchema,
    MessageCreateSchema,
    MessageFetchSchema,
    MessageIDSchema,
    UserIDSchema,
)

from . import BaseService
from .exceptions import ChatNotFoundError, InalidChatUserID, UserNotFoundError


class ChatService(BaseService):
    async def get_chats(self, *, userIDSchema: UserIDSchema) -> Iterable[ChatSchema]:
        async with self.uow as uow:
            resource = await uow.userRepository.get(userIDSchema)
            if not resource:
                raise UserNotFoundError

            return map(ChatSchema.model_validate, resource.chats)

    async def get_chats_info(
        self, *, userIDSchema: UserIDSchema
    ) -> Iterable[ChatInfoSchema]:
        async with self.uow as uow:
            resource = await uow.chatUserRepository.get_chats_info(userIDSchema)
            return map(ChatInfoSchema.model_validate, resource)

    async def get_or_create_chat(
        self, *, userIDSchema: UserIDSchema, retrieveSchema: ChatRetrieveSchema
    ) -> ChatSchema:
        if userIDSchema.id == retrieveSchema.with_user_id:
            raise InalidChatUserID(detail="Cannot create a chat with yourself")

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
                options=[selectinload(ChatRepository.model_cls.users)],
            )

            if not chatResource:
                raise ChatNotFoundError

            if userResource in chatResource.users:
                chatResource.users.clear()
            else:
                raise ChatNotFoundError

            await uow.commit()

    async def send_message(
        self, *, messageSchema: MessageCreateSchema
    ) -> MessageIDSchema:
        async with self.uow as uow:
            resource = await uow.messageRepository.add_one(messageSchema)
            await uow.commit()
            return MessageIDSchema(id=resource.id)

    async def get_messages(self, *, messageFetchSchema: MessageFetchSchema):
        async with self.uow as uow:
            await uow.messageRepository.fetch_messages(
                chat_id=ChatIDSchema(id=messageFetchSchema.chat_id),
                since=messageFetchSchema.since,
                until=messageFetchSchema.until,
                count=messageFetchSchema.count,
            )
