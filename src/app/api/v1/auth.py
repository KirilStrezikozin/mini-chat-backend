from fastapi import WebSocket

from app.api.deps import (
    ConfigDependency,
    ResponseCookieManagerDependency,
    UserAuthServiceDependency,
    UserIDDependency,
    WebSocketCookieManagerDependency,
)
from app.schemas import (
    UserIDSchema,
    UserLoginSchema,
    UserPasswordSchema,
    UserRegisterSchema,
)
from app.utils.router import APIRouterWithRouteProtection
from app.utils.security import JWTManager
from app.utils.websockets import WebSocketManager

auth_router = APIRouterWithRouteProtection(prefix="/auth", tags=["auth"])


@auth_router.post("/register")
async def register(
    payload: UserRegisterSchema,
    service: UserAuthServiceDependency,
    cookie_manager: ResponseCookieManagerDependency,
) -> None:
    tokenSchema = await service.register(registerSchema=payload)
    cookie_manager.set_token_cookie(tokenSchema)


@auth_router.post("/login")
async def login(
    payload: UserLoginSchema,
    service: UserAuthServiceDependency,
    cookie_manager: ResponseCookieManagerDependency,
) -> None:
    tokenSchema = await service.login(loginSchema=payload)
    cookie_manager.set_token_cookie(tokenSchema)


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
    await service.delete_account(idSchema=idSchema, passwordSchema=passwordSchema)
    cookie_manager.unset_token_cookie()


@auth_router.get("/token", protected=True)
async def token() -> None:
    # Protected route. It will only reach this place
    # and return status 200 if the middleware validated the token.
    pass


@auth_router.websocket("/ws")
async def websocket_endpoint(
    cookie_manager: WebSocketCookieManagerDependency, ws: WebSocket
):
    tokenPayload = cookie_manager.validate_token_cookie()
    await WebSocketManager.handle_client(
        user=UserIDSchema(id=tokenPayload.id), websocket=ws
    )


@auth_router.get("/ws/token", protected=True)
async def websocket_token(
    config: ConfigDependency,
    cookie_manager: ResponseCookieManagerDependency,
    idSchema: UserIDDependency,
) -> None:
    tokenSchema = JWTManager.create_ws_token_schema(config, idSchema)
    cookie_manager.set_ws_token_cookie(tokenSchema)
