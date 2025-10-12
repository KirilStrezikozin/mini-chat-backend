from fastapi import HTTPException

from app.api.deps import (
    ChatServiceDependency,
    UserIDDependency,
    UserProfileServiceDependency,
)
from app.schemas import (
    ChatInfoSchema,
    UserFullNameSchema,
    UserProfileSchema,
    UserUserNameSchema,
)
from app.services.exceptions import UserNameAlreadyRegistered, UserNotFoundError
from app.utils.router import APIRouterWithRouteProtection

user_router = APIRouterWithRouteProtection(prefix="/user", tags=["user"])


@user_router.get("", protected=True)
async def user(
    service: UserProfileServiceDependency,
    idSchema: UserIDDependency,
) -> UserProfileSchema:
    try:
        return await service.get_user(idSchema=idSchema)
    except UserNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail) from error


@user_router.post("/edit/fullname", protected=True)
async def edit_fullname(
    service: UserProfileServiceDependency,
    fullNameSchema: UserFullNameSchema,
    idSchema: UserIDDependency,
) -> None:
    try:
        await service.edit_fullname(
            idSchema=idSchema, new_fullname_schema=fullNameSchema
        )
    except UserNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail) from error


@user_router.post("/edit/username", protected=True)
async def edit_username(
    service: UserProfileServiceDependency,
    userNameSchema: UserUserNameSchema,
    idSchema: UserIDDependency,
) -> None:
    try:
        await service.edit_username(
            idSchema=idSchema, new_username_schema=userNameSchema
        )
    except (UserNotFoundError, UserNameAlreadyRegistered) as error:
        raise HTTPException(status_code=404, detail=error.detail) from error


@user_router.get("/chats", protected=True)
async def get_chat_info(
    service: ChatServiceDependency,
    idSchema: UserIDDependency,
) -> list[ChatInfoSchema]:
    res = await service.get_chats_info(userIDSchema=idSchema)
    return list(res)
