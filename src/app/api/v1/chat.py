from datetime import datetime

from fastapi import HTTPException

from app.api.deps import (
    ChatDiscoveryServiceDependency,
    ChatServiceDependency,
    UserIDDependency,
)
from app.schemas import (
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
from app.services.exceptions import (
    ChatNotFoundError,
    InalidChatUserID,
    UserNotFoundError,
)
from app.utils.exceptions import ClientNotConnectedError
from app.utils.router import APIRouterWithRouteProtection
from app.utils.types import IDType
from app.utils.websockets import WebSocketController

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
    res = await service.search_users(
        contains=contains, by=by, skip_id=idSchema, count=count
    )
    return list(res)


@chat_router.get("/new", protected=True)
async def get_or_create(
    service: ChatServiceDependency,
    with_user_id: IDType,
    idSchema: UserIDDependency,
) -> ChatSchema:
    try:
        return await service.get_or_create_chat(
            userIDSchema=idSchema,
            retrieveSchema=ChatRetrieveSchema(with_user_id=with_user_id),
        )
    except InalidChatUserID as error:
        raise HTTPException(status_code=400, detail=error.detail) from error


@chat_router.post("/leave", protected=True)
async def leave(
    service: ChatServiceDependency,
    chatIDSchema: ChatIDSchema,
    idSchema: UserIDDependency,
) -> None:
    try:
        await service.leave_chat(
            chatUserSchema=ChatUserSchema(
                user_id=idSchema.id,
                chat_id=chatIDSchema.id,
            )
        )
    except (UserNotFoundError, ChatNotFoundError) as error:
        raise HTTPException(status_code=404, detail=error.detail) from error


@chat_router.get("/messages", protected=True)
async def get_messages(
    service: ChatServiceDependency,
    chat_id: IDType,
    since: datetime | None = None,
    until: datetime | None = None,
    count: int | None = None,
) -> list[MessageReadSchema]:
    try:
        res = await service.get_messages(
            messageFetchSchema=MessageFetchSchema(
                chat_id=chat_id,
                since=since,
                until=until,
                count=count,
            )
        )

        return list(res)

    except ChatNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail) from error


@chat_router.post("/send", protected=True)
async def send(
    service: ChatServiceDependency,
    messageSchema: MessageSendSchema,
    idSchema: UserIDDependency,
) -> MessageReadSchema:
    newMessageSchema: MessageReadSchema

    try:
        newMessageSchema = await service.send_message(
            messageSchema=MessageCreateSchema(
                sender_id=idSchema.id,
                chat_id=messageSchema.chat_id,
                content=messageSchema.content,
            )
        )

        chat_users = await service.get_users(
            chatIDSchema=ChatIDSchema(id=messageSchema.chat_id)
        )

    except (ChatNotFoundError, UserNotFoundError) as error:
        raise HTTPException(status_code=400, detail=error.detail) from error

    try:
        await WebSocketController.announce(
            users=chat_users,
            model=MessagePutAnnouncementSchema(message=newMessageSchema),
            from_user=idSchema,
        )
    except ClientNotConnectedError:
        pass

    return newMessageSchema
