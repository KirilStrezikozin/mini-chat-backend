from fastapi import Depends, HTTPException

from app.api.deps import (
    ChatDiscoveryServiceDependency,
    ChatServiceDependency,
    get_user_id,
)
from app.schemas import (
    ChatIDSchema,
    ChatInfoSchema,
    ChatRetrieveSchema,
    ChatSchema,
    ChatSearchByType,
    ChatSearchResultSchema,
    ChatUserSchema,
    UserIDSchema,
)
from app.services.exceptions import (
    ChatNotFoundError,
    InalidChatUserID,
    UserNotFoundError,
)
from app.utils.router import APIRouterWithRouteProtection
from app.utils.types import IDType

chats_router = APIRouterWithRouteProtection(prefix="/chats", tags=["chats"])


@chats_router.get(
    "/search/{by}",
    protected=True,
    protected_hint=["/search/" + by.name for by in ChatSearchByType],
)
async def search(
    service: ChatDiscoveryServiceDependency,
    contains: str,
    by: ChatSearchByType,
    count: int | None = None,
    idSchema: UserIDSchema = Depends(get_user_id),  # noqa: B008
) -> list[ChatSearchResultSchema]:
    res = await service.search_users(
        contains=contains, by=by, skip_id=idSchema, count=count
    )
    return list(res)


@chats_router.get("/new", protected=True)
async def get_or_create(
    service: ChatServiceDependency,
    with_user_id: IDType,
    idSchema: UserIDSchema = Depends(get_user_id),  # noqa: B008
) -> ChatSchema:
    try:
        return await service.get_or_create_chat(
            userIDSchema=idSchema,
            retrieveSchema=ChatRetrieveSchema(with_user_id=with_user_id),
        )
    except InalidChatUserID as error:
        raise HTTPException(status_code=400, detail=error.detail) from error


@chats_router.post("/leave", protected=True)
async def leave_chat(
    service: ChatServiceDependency,
    chatIDSchema: ChatIDSchema,
    idSchema: UserIDSchema = Depends(get_user_id),  # noqa: B008
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


@chats_router.get("", protected=True)
async def get_chats_info(
    service: ChatServiceDependency,
    idSchema: UserIDSchema = Depends(get_user_id),  # noqa: B008
) -> list[ChatInfoSchema]:
    res = await service.get_chats_info(userIDSchema=idSchema)
    return list(res)
