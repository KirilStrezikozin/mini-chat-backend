from pydantic import BaseModel

from app.utils.types import TokenType

from . import IDSchema


class AccessTokenSchema(BaseModel):
    access_token: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class TokenSchema(AccessTokenSchema, RefreshTokenSchema):
    pass


class TokenPayload(IDSchema):
    type: TokenType
