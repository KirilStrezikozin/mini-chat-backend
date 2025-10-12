from fastapi import Depends, HTTPException

from app.api.deps import (
    ResponseCookieManagerDependency,
    UserAuthServiceDependency,
    get_user_id,
)
from app.schemas import (
    UserIDSchema,
    UserLoginSchema,
    UserPasswordSchema,
    UserRegisterSchema,
)
from app.services.exceptions import (
    UserEmailAlreadyRegistered,
    UserEmailNotFoundError,
    UserNameAlreadyRegistered,
    UserNameNotFoundError,
    UserNotFoundError,
)
from app.utils.exceptions import PasswordVerificationError
from app.utils.router import APIRouterWithRouteProtection

auth_router = APIRouterWithRouteProtection(prefix="/auth", tags=["auth"])


@auth_router.post("/register")
async def register(
    payload: UserRegisterSchema,
    service: UserAuthServiceDependency,
    cookie_manager: ResponseCookieManagerDependency,
) -> None:
    try:
        tokenSchema = await service.register(registerSchema=payload)
        cookie_manager.set_token_cookie(tokenSchema)

    except (UserEmailAlreadyRegistered, UserNameAlreadyRegistered) as error:
        raise HTTPException(status_code=409, detail=error.detail) from error


@auth_router.post("/login")
async def login(
    payload: UserLoginSchema,
    service: UserAuthServiceDependency,
    cookie_manager: ResponseCookieManagerDependency,
) -> None:
    try:
        tokenSchema = await service.login(loginSchema=payload)
        cookie_manager.set_token_cookie(tokenSchema)

    except (
        UserNameNotFoundError,
        UserEmailNotFoundError,
        PasswordVerificationError,
    ) as error:
        raise HTTPException(
            status_code=401, detail="Username, email, or password is incorrect"
        ) from error


@auth_router.post("/logout", protected=True)
async def logout(
    cookie_manager: ResponseCookieManagerDependency,
) -> None:
    cookie_manager.unset_token_cookie()


@auth_router.post("/delete-account", protected=True)
async def delete_account(
    service: UserAuthServiceDependency,
    cookie_manager: ResponseCookieManagerDependency,
    passwordSchema: UserPasswordSchema,
    idSchema: UserIDSchema = Depends(get_user_id),  # noqa: B008
) -> None:
    try:
        await service.delete_account(idSchema=idSchema, passwordSchema=passwordSchema)
        cookie_manager.unset_token_cookie()

    except UserNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail) from error
    except PasswordVerificationError as error:
        raise HTTPException(status_code=404, detail="Incorrect password") from error


@auth_router.get("/token", protected=True)
async def token() -> None:
    # Protected route. It will only reach this place
    # and return status 200 if the middleware validated the token.
    pass
