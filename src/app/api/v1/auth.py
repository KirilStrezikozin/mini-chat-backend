from fastapi import APIRouter, WebSocket

from app.api.deps import (
    ConfigDependency,
    HTTPResponseCookieManagerDependency,
    UserAuthServiceDependency,
    UserIDDependency,
    WebSocketCookieManagerDependency,
)
from app.core.router import ProtectedAPIRouter
from app.schemas import (
    UserIDSchema,
    UserLoginSchema,
    UserRegisterSchema,
)
from app.utils.security import JWTManager
from app.utils.websockets import WebSocketManager

unprotected_router = APIRouter(prefix="/auth", tags=["auth"])
protected_router = ProtectedAPIRouter(prefix="/auth", tags=["auth"])


@unprotected_router.post("/register")
async def register(
    service: UserAuthServiceDependency,
    cookie_manager: HTTPResponseCookieManagerDependency,
    register_schema: UserRegisterSchema,
) -> None:
    tokenSchema = await service.register(register_schema=register_schema)
    cookie_manager.set_token_cookie(tokenSchema)


@unprotected_router.post("/login")
async def login(
    service: UserAuthServiceDependency,
    cookie_manager: HTTPResponseCookieManagerDependency,
    login_schema: UserLoginSchema,
) -> None:
    token_schema = await service.login(login_schema=login_schema)
    cookie_manager.set_token_cookie(token_schema)


@protected_router.post("/logout")
async def logout(
    cookie_manager: HTTPResponseCookieManagerDependency,
) -> None:
    cookie_manager.unset_token_cookie()


@protected_router.get("/validate")
async def validate() -> None:
    # Protected route. It will only reach this place
    # and return status 200 if the middleware validated the token.
    pass


@unprotected_router.websocket("/ws")
async def websocket_endpoint(
    cookie_manager: WebSocketCookieManagerDependency, ws: WebSocket
):
    token_payload = cookie_manager.validate_token_cookie()
    await WebSocketManager.handle_client(
        user=UserIDSchema(id=token_payload.id), websocket=ws
    )


@protected_router.get("/ws/token")
async def websocket_token(
    config: ConfigDependency,
    cookie_manager: HTTPResponseCookieManagerDependency,
    user_schema: UserIDDependency,
) -> None:
    token_schema = JWTManager.create_ws_token_schema(config, user_schema)
    cookie_manager.set_ws_token_cookie(token_schema)
