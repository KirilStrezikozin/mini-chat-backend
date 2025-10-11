from fastapi import Response

from app.core.config import Config
from app.schemas import TokenSchema, TokenType


class ResponseCookieManager:
    def __init__(self, config: Config, response: Response) -> None:
        self.config = config
        self.response = response

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
