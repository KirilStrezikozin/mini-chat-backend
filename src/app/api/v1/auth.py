from fastapi import HTTPException, WebSocket

from app.api.deps import (
    ConfigDependency,
    ResponseCookieManagerDependency,
    UserAuthServiceDependency,
    UserIDDependency,
    WebSocketCookieManagerDependency,
)
from app.core.logger import logger
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
from app.utils.exceptions import (
    PasswordVerificationError,
    TokenValidationError,
    WebSocketClientAlreadyConnected,
)
from app.utils.router import APIRouterWithRouteProtection
from app.utils.security import JWTManager
from app.utils.websockets import WebSocketConnectionManager

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
    idSchema: UserIDDependency,
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


@auth_router.websocket("/ws")
async def websocket_endpoint(
    cookie_manager: WebSocketCookieManagerDependency, ws: WebSocket
):
    try:
        tokenPayload = cookie_manager.validate_token_cookie()
    except TokenValidationError:
        await ws.close(code=1000)
        return

    def recv_callback(payload: object):
        logger.info(
            f"{WebSocketConnectionManager.__name__}: client",
            tokenPayload.id,
            "received data:",
            payload,
        )

    try:
        await WebSocketConnectionManager.handle_connection(
            user=UserIDSchema(id=tokenPayload.id),
            websocket=ws,
            recv_callback=recv_callback,
        )
    except WebSocketClientAlreadyConnected:
        logger.info(
            f"{WebSocketConnectionManager.__name__}: client",
            tokenPayload.id,
            "already connected",
        )

        await ws.close(code=1000)
        return


@auth_router.get("/ws/token", protected=True)
async def websocket_token(
    config: ConfigDependency,
    cookie_manager: ResponseCookieManagerDependency,
    idSchema: UserIDDependency,
) -> None:
    tokenSchema = JWTManager.create_ws_token_schema(config, idSchema)
    cookie_manager.set_ws_token_cookie(tokenSchema)
