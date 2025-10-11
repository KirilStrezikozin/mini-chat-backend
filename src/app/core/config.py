import logging
import secrets
import warnings
from pathlib import Path
from typing import Self

from pydantic import BaseModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.db.configs import PostgresDsnConfig


class TokenConfig(BaseModel):
    ACCESS_EXPIRES_SECONDS: int = 15 * 60
    REFRESH_EXPIRES_SECONDS: int = 7 * 24 * 60 * 60
    WS_EXPIRES_SECONDS: int = 15


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent.parent / ".env",
        env_ignore_empty=True,
        extra="forbid",
        case_sensitive=False,
        env_nested_delimiter="__",
    )

    PROJECT_NAME: str
    PREFIX_API_V1: str = "/api/v1"
    SECRET_KEY: str = ""
    SECRET_KEY_ALGORITHM: str = "HS256"

    SITE_URL: str
    ALLOW_ORIGINS: list[str]
    USE_SECURE_COOKIES: bool = True

    FRONTEND_PORT: int = 3000
    BACKEND_PORT: int = 8000
    BACKEND_HOST: str = "localhost"
    BACKEND_URL: str = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
    FRONTEND_URL: str = "http://localhost:3000"

    token: TokenConfig = TokenConfig()
    database: PostgresDsnConfig  # Preferred db configuration

    @model_validator(mode="after")
    def _ensure_has_secret_key(self) -> Self:
        if not self.SECRET_KEY:
            self.SECRET_KEY = secrets.token_urlsafe(32)
            warnings.warn(
                "New SECRET_KEY has been generated. Store it in .env "
                "to avoid invalidating tokens between app restarts",
                stacklevel=1,
            )
        return self

    @model_validator(mode="after")
    def _configure_logger(self) -> Self:
        logging.basicConfig(level=logging.INFO)
        return self


def newConfig() -> Config:
    """
    Returns a new application configuration instance.
    """
    return Config()  # type: ignore


config = newConfig()
