from enum import Enum

from app.utils.types import IDType

from . import Base, IDSchema
from .user import UserFullNameSchema, UserIDSchema, UserUserNameSchema


class ChatIDSchema(IDSchema):
    pass


class ChatSchema(ChatIDSchema):
    pass


class ChatUserSchema(Base):
    user_id: IDType
    chat_id: IDType


class ChatRetrieveSchema(Base):
    with_user_id: IDType


class ChatSearchByType(str, Enum):
    fullname = "fullname"
    username = "username"


class ChatSearchResultSchema(UserIDSchema, UserFullNameSchema, UserUserNameSchema):
    pass


class ChatInfoSchema(UserIDSchema, UserFullNameSchema, UserUserNameSchema):
    chat_id: IDType
