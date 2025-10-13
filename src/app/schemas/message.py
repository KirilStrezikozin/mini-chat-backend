from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import StringConstraints, model_validator

from app.utils.types import IDType

from . import Base, IDSchema


class MessageIDSchema(IDSchema):
    pass


class MessageContentSchema(Base):
    content: Annotated[str, StringConstraints(max_length=5000)]


class MessageTimestampSchema(Base):
    timestamp: datetime


class MessageSendSchema(MessageContentSchema):
    chat_id: IDType


class MessageCreateSchema(MessageSendSchema):
    sender_id: IDType


class MessageReadSchema(MessageIDSchema, MessageTimestampSchema, MessageCreateSchema):
    pass


class MessageDeleteSchema(MessageIDSchema):
    chat_id: IDType


class MessageChangeContentSchema(MessageIDSchema, MessageContentSchema):
    pass


class MessageEditSchema(MessageContentSchema, MessageIDSchema):
    pass


class MessagePutAnnouncementSchema(Base):
    announcement_type: Literal["message/put"] = "message/put"
    message: MessageReadSchema


class MessageDeleteAnnouncementSchema(Base):
    announcement_type: Literal["message/delete"] = "message/delete"
    message: MessageDeleteSchema


class MessageFetchSchema(Base):
    chat_id: IDType
    since: datetime | None = None
    until: datetime | None = None
    count: int | None = None

    @model_validator(mode="after")
    def check(self) -> Self:
        if not any(
            [
                self.since and self.count,
                self.until and self.count,
                self.since and self.until and not self.count,
            ]
        ):
            raise ValueError("invalid arguments")
        return self
