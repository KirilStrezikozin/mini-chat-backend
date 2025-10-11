from fastapi import APIRouter, HTTPException

from app.api.deps import (
    ResponseCookieManagerDependency,
    UserAuthServiceDependency,
)
from app.schemas import UserLoginSchema, UserRegisterSchema
from app.services.exceptions import (
    UserEmailAlreadyRegistered,
    UserEmailNotFoundError,
    UserNameAlreadyRegistered,
    UserNameNotFoundError,
)
from app.utils.exceptions import PasswordVerificationError

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register")
async def register(
    payload: UserRegisterSchema,
    service: UserAuthServiceDependency,
    cookie_manager: ResponseCookieManagerDependency,
) -> None:
    try:
        tokenSchema = await service.register(registerSchema=payload)
        cookie_manager.set_token_cookie(tokenSchema)

    except UserEmailAlreadyRegistered as error:
        raise HTTPException(
            status_code=409, detail="A user with this email already exists"
        ) from error
    except UserNameAlreadyRegistered as error:
        raise HTTPException(
            status_code=409, detail="A user with this username already exists"
        ) from error


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


@auth_router.post("/logout")
async def logout(
    cookie_manager: ResponseCookieManagerDependency,
) -> None:
    cookie_manager.unset_token_cookie()


@auth_router.get("/token")
async def token() -> None:
    # Protected route. It will only reach this place
    # and return status 200 if the middleware validated the token.
    pass
