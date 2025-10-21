from app.api.deps import (
    ChatServiceDependency,
    HTTPResponseCookieManagerDependency,
    UserAuthServiceDependency,
    UserIDDependency,
    UserProfileServiceDependency,
)
from app.core.router import ProtectedAPIRouter
from app.schemas import (
    ChatInfoSchema,
    UserFullNameSchema,
    UserPasswordSchema,
    UserProfileSchema,
    UserUserNameSchema,
)

protected_router = ProtectedAPIRouter(prefix="/user", tags=["user"])


@protected_router.get("")
async def user(
    service: UserProfileServiceDependency,
    user_schema: UserIDDependency,
) -> UserProfileSchema:
    return await service.get_user_profile(user_schema=user_schema)


@protected_router.patch("/fullname")
async def edit_fullname(
    service: UserProfileServiceDependency,
    user_schema: UserIDDependency,
    fullname_schema: UserFullNameSchema,
) -> UserProfileSchema:
    return await service.patch_fullname(
        user_schema=user_schema, fullname_schema=fullname_schema
    )


@protected_router.patch("/username")
async def edit_username(
    service: UserProfileServiceDependency,
    user_schema: UserIDDependency,
    username_schema: UserUserNameSchema,
) -> UserProfileSchema:
    return await service.patch_username(
        user_schema=user_schema, username_schema=username_schema
    )


@protected_router.delete("")
async def delete_user_account(
    service: UserAuthServiceDependency,
    cookie_manager: HTTPResponseCookieManagerDependency,
    user_schema: UserIDDependency,
    password_schema: UserPasswordSchema,
) -> None:
    await service.delete_user_account(
        user_schema=user_schema, password_schema=password_schema
    )
    cookie_manager.unset_token_cookie()


@protected_router.get("/chats")
async def get_chats_info(
    service: ChatServiceDependency,
    user_schema: UserIDDependency,
) -> list[ChatInfoSchema]:
    return await service.get_chats_info(user_schema=user_schema)
