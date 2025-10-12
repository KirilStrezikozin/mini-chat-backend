from typing import Annotated

from fastapi import Depends, Request, Response, WebSocket

from app.core.config import Config, config
from app.db.session import async_session_factory
from app.schemas import TokenPayload, UserIDSchema
from app.services import (
    ChatDiscoveryService,
    ChatService,
    UserAuthService,
    UserProfileService,
)
from app.utils.security import JWTManager, ResponseCookieManager, WebSocketCookieManager
from app.utils.uow import AsyncUnitOfWork


def get_config() -> Config:
    return config


ConfigDependency = Annotated[Config, Depends(get_config)]


def get_uow(request: Request) -> AsyncUnitOfWork:
    engine = request.app.state.engine
    return AsyncUnitOfWork(async_session_factory=async_session_factory(engine))


UoWDependency = Annotated[AsyncUnitOfWork, Depends(get_uow)]


def get_user_auth_service(
    uow: UoWDependency, config: ConfigDependency
) -> UserAuthService:
    return UserAuthService(config, uow)


UserAuthServiceDependency = Annotated[UserAuthService, Depends(get_user_auth_service)]


def get_chat_discovery_service(
    uow: UoWDependency, config: ConfigDependency
) -> ChatDiscoveryService:
    return ChatDiscoveryService(config, uow)


ChatDiscoveryServiceDependency = Annotated[
    ChatDiscoveryService, Depends(get_chat_discovery_service)
]


def get_user_profile_service(
    uow: UoWDependency, config: ConfigDependency
) -> UserProfileService:
    return UserProfileService(config, uow)


UserProfileServiceDependency = Annotated[
    UserProfileService, Depends(get_user_profile_service)
]


def get_chat_service(uow: UoWDependency, config: ConfigDependency) -> ChatService:
    return ChatService(config, uow)


ChatServiceDependency = Annotated[ChatService, Depends(get_chat_service)]


def get_token_payload(request: Request) -> TokenPayload:
    return JWTManager.get_request_token_payload(request)


RequestTokenPayloadDependency = Annotated[TokenPayload, Depends(get_token_payload)]


def get_user_id(tokenPayload: RequestTokenPayloadDependency) -> UserIDSchema:
    return UserIDSchema(id=tokenPayload.id)


UserIDDependency = Annotated[UserIDSchema, Depends(get_user_id)]


def get_cookie_manager(
    response: Response, config: ConfigDependency
) -> ResponseCookieManager:
    return ResponseCookieManager(config, response)


ResponseCookieManagerDependency = Annotated[
    ResponseCookieManager, Depends(get_cookie_manager)
]


def get_websocket_cookie_manager(
    config: ConfigDependency, ws: WebSocket
) -> WebSocketCookieManager:
    return WebSocketCookieManager(config, ws)


WebSocketCookieManagerDependency = Annotated[
    WebSocketCookieManager, Depends(get_websocket_cookie_manager)
]
