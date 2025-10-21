from typing import Annotated

from fastapi import Depends, Request, Response, WebSocket

from app.core.config import Config, config
from app.db.session import async_session_factory
from app.interfaces.utils.s3.client import S3ClientProtocol
from app.interfaces.utils.uow import AbstractAsyncUnitOfWork
from app.schemas import TokenPayload, UserIDSchema
from app.services import (
    AttachmentService,
    ChatDiscoveryService,
    ChatService,
    MessageService,
    UserAuthService,
    UserProfileService,
)
from app.utils.security import (
    HTTPResponseCookieManager,
    JWTManager,
    WebSocketCookieManager,
)
from app.utils.uow import AsyncUnitOfWork


def get_config() -> Config:
    return config


ConfigDependency = Annotated[Config, Depends(get_config)]


def get_uow(request: Request) -> AbstractAsyncUnitOfWork:
    engine = request.app.state.engine
    return AsyncUnitOfWork(async_session_factory=async_session_factory(engine))


UoWDependency = Annotated[AbstractAsyncUnitOfWork, Depends(get_uow)]


def get_s3_client(request: Request) -> S3ClientProtocol:
    return request.app.state.s3_client


S3ClientDependency = Annotated[S3ClientProtocol, Depends(get_s3_client)]


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


def get_message_service(uow: UoWDependency, config: ConfigDependency) -> MessageService:
    return MessageService(config, uow)


MessageServiceDependency = Annotated[MessageService, Depends(get_message_service)]


def get_attachment_service(
    uow: UoWDependency, config: ConfigDependency, s3: S3ClientDependency
) -> AttachmentService:
    return AttachmentService(config, uow, s3)


AttachmentServiceDependency = Annotated[
    AttachmentService, Depends(get_attachment_service)
]


def get_token_payload(request: Request) -> TokenPayload:
    return JWTManager.get_request_token_payload(request)


RequestTokenPayloadDependency = Annotated[TokenPayload, Depends(get_token_payload)]


def get_user_id(tokenPayload: RequestTokenPayloadDependency) -> UserIDSchema:
    return UserIDSchema(id=tokenPayload.id)


UserIDDependency = Annotated[UserIDSchema, Depends(get_user_id)]


def get_http_response_cookie_manager(
    response: Response, config: ConfigDependency
) -> HTTPResponseCookieManager:
    return HTTPResponseCookieManager(config, response)


HTTPResponseCookieManagerDependency = Annotated[
    HTTPResponseCookieManager, Depends(get_http_response_cookie_manager)
]


def get_websocket_cookie_manager(
    config: ConfigDependency, ws: WebSocket
) -> WebSocketCookieManager:
    return WebSocketCookieManager(config, ws)


WebSocketCookieManagerDependency = Annotated[
    WebSocketCookieManager, Depends(get_websocket_cookie_manager)
]
