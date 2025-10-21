from datetime import datetime

from app.api.deps import (
    AttachmentServiceDependency,
    ChatDiscoveryServiceDependency,
    ChatServiceDependency,
    UserIDDependency,
)
from app.core.router import ProtectedAPIRouter
from app.schemas import (
    AttachmentReadSchema,
    ChatIDSchema,
    ChatRetrieveSchema,
    ChatSchema,
    ChatSearchByType,
    ChatSearchResultSchema,
    MessageCreateSchema,
    MessageFetchSchema,
    MessagePutAnnouncementSchema,
    MessageReadSchema,
    MessageSendSchema,
)
from app.utils.types import IDType
from app.utils.websockets import WebSocketManager

protected_router = ProtectedAPIRouter(prefix="/chats", tags=["chats"])


@protected_router.get("/search")
async def search(
    chat_discovery_service: ChatDiscoveryServiceDependency,
    user_schema: UserIDDependency,
    contains: str,
    by: ChatSearchByType,
    count: int | None = None,
) -> list[ChatSearchResultSchema]:
    return await chat_discovery_service.search_users(
        contains=contains, by=by, skip_id=user_schema, count=count
    )


@protected_router.post("")
async def get_or_create(
    chat_service: ChatServiceDependency,
    user_schema: UserIDDependency,
    with_user_schema: ChatRetrieveSchema,
) -> ChatSchema:
    return await chat_service.get_or_create(
        user_schema=user_schema, retrieve_schema=with_user_schema
    )


@protected_router.post("/{id}/leave")
async def leave(
    chat_service: ChatServiceDependency,
    id: IDType,
    user_schema: UserIDDependency,
) -> None:
    await chat_service.leave(user_schema=user_schema, chat_schema=ChatIDSchema(id=id))


@protected_router.get("/{id}/messages")
async def get_messages(
    chat_service: ChatServiceDependency,
    id: IDType,
    since: datetime | None = None,
    until: datetime | None = None,
    count: int | None = None,
) -> list[MessageReadSchema]:
    return await chat_service.get_messages(
        message_fetch_schema=MessageFetchSchema(
            chat_id=id,
            since=since,
            until=until,
            count=count,
        )
    )


@protected_router.get("/{id}/attachments")
async def get_attachments(
    id: IDType,
    attachment_service: AttachmentServiceDependency,
) -> list[AttachmentReadSchema]:
    return await attachment_service.get_all_in_chat(chat_schema=ChatIDSchema(id=id))


@protected_router.post("/{id}/send")
async def send(
    chat_service: ChatServiceDependency,
    id: IDType,
    message_schema: MessageSendSchema,
    user_schema: UserIDDependency,
) -> MessageReadSchema:
    message_schema = MessageCreateSchema(
        sender_id=user_schema.id, chat_id=id, content=message_schema.content
    )

    message = await chat_service.send_message(
        user_schema=user_schema, message_schema=message_schema
    )

    chat_users = await chat_service.get_users(chat_schema=ChatIDSchema(id=id))

    await WebSocketManager.announce(
        users=chat_users,
        model=MessagePutAnnouncementSchema(message=message),
    )

    return message
