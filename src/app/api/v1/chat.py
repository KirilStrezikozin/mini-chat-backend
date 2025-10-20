from datetime import datetime

from app.api.deps import (
    AttachmentServiceDependency,
    ChatDiscoveryServiceDependency,
    ChatServiceDependency,
    UserIDDependency,
)
from app.schemas import (
    AttachmentReadSchema,
    ChatIDSchema,
    ChatRetrieveSchema,
    ChatSchema,
    ChatSearchByType,
    ChatSearchResultSchema,
    ChatUserSchema,
    MessageCreateSchema,
    MessageFetchSchema,
    MessagePutAnnouncementSchema,
    MessageReadSchema,
    MessageSendSchema,
)
from app.utils.router import APIRouterWithRouteProtection
from app.utils.types import IDType
from app.utils.websockets import WebSocketManager

chat_router = APIRouterWithRouteProtection(prefix="/chat", tags=["chat"])


@chat_router.get(
    "/search/{by}",
    protected=True,
    protected_hint=["/search/" + by.name for by in ChatSearchByType],
)
async def search(
    service: ChatDiscoveryServiceDependency,
    idSchema: UserIDDependency,
    contains: str,
    by: ChatSearchByType,
    count: int | None = None,
) -> list[ChatSearchResultSchema]:
    return await service.search_users(
        contains=contains, by=by, skip_id=idSchema, count=count
    )


@chat_router.get("/new", protected=True)
async def get_or_create(
    service: ChatServiceDependency,
    with_user_id: IDType,
    idSchema: UserIDDependency,
) -> ChatSchema:
    return await service.get_or_create_chat(
        userIDSchema=idSchema,
        retrieveSchema=ChatRetrieveSchema(with_user_id=with_user_id),
    )


@chat_router.post("/leave", protected=True)
async def leave(
    service: ChatServiceDependency,
    chatIDSchema: ChatIDSchema,
    idSchema: UserIDDependency,
) -> None:
    await service.leave_chat(
        chatUserSchema=ChatUserSchema(
            user_id=idSchema.id,
            chat_id=chatIDSchema.id,
        )
    )


@chat_router.get("/messages", protected=True)
async def get_messages(
    service: ChatServiceDependency,
    chat_id: IDType,
    since: datetime | None = None,
    until: datetime | None = None,
    count: int | None = None,
) -> list[MessageReadSchema]:
    return await service.get_messages(
        messageFetchSchema=MessageFetchSchema(
            chat_id=chat_id,
            since=since,
            until=until,
            count=count,
        )
    )


@chat_router.post("/send", protected=True)
async def send(
    service: ChatServiceDependency,
    messageSchema: MessageSendSchema,
    idSchema: UserIDDependency,
) -> MessageReadSchema:
    newMessageSchema = await service.send_message(
        messageSchema=MessageCreateSchema(
            sender_id=idSchema.id,
            chat_id=messageSchema.chat_id,
            content=messageSchema.content,
        ),
    )

    chat_users = await service.get_users(
        chatIDSchema=ChatIDSchema(id=messageSchema.chat_id)
    )

    await WebSocketManager.announce(
        users=chat_users,
        model=MessagePutAnnouncementSchema(message=newMessageSchema),
    )

    return newMessageSchema


@chat_router.get("/attachments", protected=True)
async def get_attachments(
    chat_id: IDType,
    service: AttachmentServiceDependency,
) -> list[AttachmentReadSchema]:
    return await service.get_all_in_chat(chat_schema=ChatIDSchema(id=chat_id))
