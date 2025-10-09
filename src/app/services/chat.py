from collections.abc import Iterable

from app.schemas import (
    ChatIDSchema,
    ChatRetrieveSchema,
    ChatSchema,
    ChatUserSchema,
    MessageCreateSchema,
    MessageFetchSchema,
    MessageIDSchema,
    UserIDSchema,
)

from . import BaseService
from .exceptions import ChatNotFoundError, UserNotFoundError


class ChatService(BaseService):
    async def get_chats(self, *, userIDSchema: UserIDSchema) -> Iterable[ChatSchema]:
        async with self.uow as uow:
            resource = await uow.userRepository.get(userIDSchema)
            if not resource:
                raise UserNotFoundError
            return map(ChatSchema.model_validate, resource.chats)

    async def get_or_create_chat(
        self, *, retrieveSchema: ChatRetrieveSchema
    ) -> ChatSchema:
        async with self.uow as uow:
            chatResource = await uow.chatUserRepository.get_chat(retrieveSchema)
            if chatResource:
                return ChatSchema.model_validate(chatResource)

            userResource = await uow.userRepository.get(
                UserIDSchema(id=retrieveSchema.user_id)
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
                ChatIDSchema(id=chatUserSchema.chat_id)
            )
            if not chatResource:
                raise ChatNotFoundError

            chatResource.users.remove(userResource)
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
