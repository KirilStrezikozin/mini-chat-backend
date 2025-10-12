from enum import Enum

from . import Base, IDSchema


class AccessTokenSchema(Base):
    access_token: str


class RefreshTokenSchema(Base):
    refresh_token: str


class TokenSchema(AccessTokenSchema, RefreshTokenSchema):
    pass


class WebsocketTokenSchema(Base):
    ws_access_token: str


class TokenType(str, Enum):
    access_token = "access_token"
    refresh_token = "refresh_token"
    ws_access_token = "ws_access_token"


class TokenPayload(IDSchema):
    type: TokenType
