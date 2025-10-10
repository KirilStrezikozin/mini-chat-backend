from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt
from pydantic import ValidationError

from app.core.config import Config
from app.schemas.token import TokenPayload, TokenSchema
from app.schemas.user import UserIDSchema
from app.utils.exceptions import (
    InstantiationNotAllowedError,
    PasswordVerificationError,
    TokenValidationError,
)
from app.utils.types import TokenType


class PasswordManager:
    def __init__(self) -> None:
        raise InstantiationNotAllowedError(self.__class__.__name__)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> None:
        if not bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        ):
            raise PasswordVerificationError

    @staticmethod
    def get_password_hash(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


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
    def validate_token(
        config: Config, token: str | bytes, tokenType: TokenType
    ) -> TokenPayload:
        try:
            payload = TokenPayload(**JWTManager.decode(config, token))
            if payload.type != tokenType:
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
    def create_refresh_token(config: Config, sub: dict) -> str:
        return JWTManager.encode(
            config,
            sub,
            expires_in=timedelta(seconds=config.token.REFRESH_EXPIRES_SECONDS),
        )

    @staticmethod
    def create_token_schema(config: Config, idSchema: UserIDSchema) -> TokenSchema:
        access_token = JWTManager.create_access_token(
            config,
            sub={"id": idSchema.id, "type": "access"},
        )
        refresh_token = JWTManager.create_refresh_token(
            config,
            sub={"id": idSchema.id, "type": "refresh"},
        )

        return TokenSchema(access_token=access_token, refresh_token=refresh_token)
