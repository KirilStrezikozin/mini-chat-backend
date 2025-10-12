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
from app.utils.websockets import WebsocketConnectionManager

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
    try:
        newMessageSchema = await service.send_message(
            messageSchema=MessageCreateSchema(
                sender_id=idSchema.id,
                chat_id=messageSchema.chat_id,
                content=messageSchema.content,
            )
        )

        chatUserIds = await service.get_users(
            chatIDSchema=ChatIDSchema(id=messageSchema.chat_id)
        )

        for userIDSchema in chatUserIds:
            if userIDSchema.id == idSchema.id:
                continue
            if not WebsocketConnectionManager.is_connected(userIDSchema):
                continue

            await WebsocketConnectionManager.send_to(
                userIDSchema, newMessageSchema.model_dump_json()
            )

        return newMessageSchema

    except (ChatNotFoundError, UserNotFoundError) as error:
        raise HTTPException(status_code=400, detail=error.detail) from error
    except ClientNotConnectedError:
        raise
