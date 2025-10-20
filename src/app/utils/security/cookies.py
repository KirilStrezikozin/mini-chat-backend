from fastapi import Response, WebSocket

from app.core.config import Config
from app.core.exceptions import TokenValidationError
from app.schemas import TokenPayload, TokenSchema, TokenType, WebSocketTokenSchema

from .jwt import JWTManager


class WebSocketCookieManager:
    def __init__(self, config: Config, ws: WebSocket) -> None:
        self.config = config
        self.ws = ws

    def validate_token_cookie(self) -> TokenPayload:
        token = self.ws.cookies.get(TokenType.ws_access_token.value)
        if token is None:
            raise TokenValidationError
        return JWTManager.validate_token(self.config, token, TokenType.ws_access_token)


class ResponseCookieManager:
    def __init__(self, config: Config, response: Response) -> None:
        self.config = config
        self.response = response

    def set_ws_token_cookie(self, tokenSchema: WebSocketTokenSchema) -> None:
        self.response.set_cookie(
            key=TokenType.ws_access_token.value,
            value=tokenSchema.ws_access_token,
            httponly=True,
            secure=self.config.USE_SECURE_COOKIES,
            max_age=self.config.token.WS_EXPIRES_SECONDS,
        )

    def set_token_cookie(self, tokenSchema: TokenSchema) -> None:
        self.response.set_cookie(
            key=TokenType.access_token.value,
            value=tokenSchema.access_token,
            httponly=True,
            secure=self.config.USE_SECURE_COOKIES,
            max_age=self.config.token.ACCESS_EXPIRES_SECONDS,
        )
        self.response.set_cookie(
            key=TokenType.refresh_token.value,
            value=tokenSchema.refresh_token,
            httponly=True,
            secure=self.config.USE_SECURE_COOKIES,
            max_age=self.config.token.REFRESH_EXPIRES_SECONDS,
        )

    def unset_token_cookie(self) -> None:
        self.response.delete_cookie(key=TokenType.access_token.value)
        self.response.delete_cookie(key=TokenType.refresh_token.value)
        self.response.delete_cookie(key=TokenType.ws_access_token.value)
