from app.utils.types import IDType

from . import Base, IDSchema


class ChatIDSchema(IDSchema):
    pass


class ChatSchema(ChatIDSchema):
    pass


class ChatUserSchema(Base):
    user_id: IDType
    chat_id: IDType


class ChatRetrieveSchema(Base):
    user_id: IDType
    with_user_id: IDType
