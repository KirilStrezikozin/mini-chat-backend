from pydantic import BaseModel

from app.utils.types import IDType

from . import IDSchema


class ChatIDSchema(IDSchema):
    pass


class ChatSchema(ChatIDSchema):
    pass


class ChatUserSchema(BaseModel):
    user_id: IDType
    chat_id: IDType


class ChatRetrieveSchema(BaseModel):
    user_id: IDType
    with_user_id: IDType
