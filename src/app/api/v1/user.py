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
from app.utils.router import APIRouterWithRouteProtection

user_router = APIRouterWithRouteProtection(prefix="/user", tags=["user"])


@user_router.get("", protected=True)
async def user(
    service: UserProfileServiceDependency,
    idSchema: UserIDDependency,
) -> UserProfileSchema:
    return await service.get_user(idSchema=idSchema)


@user_router.post("/edit/fullname", protected=True)
async def edit_fullname(
    service: UserProfileServiceDependency,
    fullNameSchema: UserFullNameSchema,
    idSchema: UserIDDependency,
) -> None:
    await service.edit_fullname(idSchema=idSchema, new_fullname_schema=fullNameSchema)


@user_router.post("/edit/username", protected=True)
async def edit_username(
    service: UserProfileServiceDependency,
    userNameSchema: UserUserNameSchema,
    idSchema: UserIDDependency,
) -> None:
    await service.edit_username(idSchema=idSchema, new_username_schema=userNameSchema)


@user_router.get("/chats", protected=True)
async def get_chat_info(
    service: ChatServiceDependency,
    idSchema: UserIDDependency,
) -> list[ChatInfoSchema]:
    return await service.get_chats_info(userIDSchema=idSchema)
