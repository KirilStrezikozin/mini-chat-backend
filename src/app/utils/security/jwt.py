from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Request
from jose import JWTError, jwt
from pydantic import ValidationError

from app.core.config import Config
from app.core.exceptions import (
    InstantiationNotAllowedError,
    TokenValidationError,
)
from app.schemas import (
    TokenPayload,
    TokenSchema,
    TokenType,
    UserIDSchema,
    WebSocketTokenSchema,
)


class JWTManager:
    def __init__(self) -> None:
        raise InstantiationNotAllowedError(self.__class__.__name__)

    @staticmethod
    def decode(config: Config, token: str | bytes) -> dict[str, Any]:
        try:
            return jwt.decode(
                token, config.SECRET_KEY, algorithms=[config.SECRET_KEY_ALGORITHM]
            )
        except (JWTError, ValidationError) as error:
            raise TokenValidationError from error

    @staticmethod
    def set_request_token_payload(request: Request, tokenPayload: TokenPayload):
        request.scope["tokenPayload"] = tokenPayload

    @staticmethod
    def get_request_token_payload(request: Request) -> TokenPayload:
        # Middleware is guaranteed to set it for protected routes,
        # thus not an optional return type.
        return request.scope["tokenPayload"]

    @staticmethod
    def validate_token(
        config: Config, token: str | bytes, tokenType: TokenType
    ) -> TokenPayload:
        try:
            payload = TokenPayload(**JWTManager.decode(config, token))
            if payload.type != tokenType.value:
                raise TokenValidationError
            return payload
        except ValidationError as error:
            raise TokenValidationError from error

    @staticmethod
    def encode(config: Config, sub: dict[str, Any], *, expires_in: timedelta) -> str:
        expiry = datetime.now(UTC) + expires_in
        claims = sub.copy()
        claims.update(exp=expiry)
        return jwt.encode(
            claims,
            config.SECRET_KEY,
            algorithm=config.SECRET_KEY_ALGORITHM,
        )

    @staticmethod
    def create_access_token(config: Config, sub: dict[str, Any]) -> str:
        return JWTManager.encode(
            config,
            sub,
            expires_in=timedelta(seconds=config.token.ACCESS_EXPIRES_SECONDS),
        )

    @staticmethod
    def create_refresh_token(config: Config, sub: dict[str, Any]) -> str:
        return JWTManager.encode(
            config,
            sub,
            expires_in=timedelta(seconds=config.token.REFRESH_EXPIRES_SECONDS),
        )

    @staticmethod
    def create_ws_access_token(config: Config, sub: dict[str, Any]) -> str:
        return JWTManager.encode(
            config,
            sub,
            expires_in=timedelta(seconds=config.token.WS_EXPIRES_SECONDS),
        )

    @staticmethod
    def create_token_schema(config: Config, idSchema: UserIDSchema) -> TokenSchema:
        access_token = JWTManager.create_access_token(
            config,
            sub={"id": str(idSchema.id), "type": TokenType.access_token.value},
        )
        refresh_token = JWTManager.create_refresh_token(
            config,
            sub={"id": str(idSchema.id), "type": TokenType.refresh_token.value},
        )

        return TokenSchema(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def create_ws_token_schema(
        config: Config, idSchema: UserIDSchema
    ) -> WebSocketTokenSchema:
        ws_access_token = JWTManager.create_ws_access_token(
            config,
            sub={"id": str(idSchema.id), "type": TokenType.ws_access_token.value},
        )
        return WebSocketTokenSchema(ws_access_token=ws_access_token)
