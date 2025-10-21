from collections.abc import Sequence
from datetime import datetime
from typing import Annotated, Self

from pydantic import StringConstraints, model_validator

from app.utils.types import IDType

from . import Base, IDSchema
from .attachment import AttachmentReadSchema


class MessageIDSchema(IDSchema):
    pass


class MessageContentSchema(Base):
    content: Annotated[str, StringConstraints(max_length=5000)]


class MessageTimestampSchema(Base):
    timestamp: datetime


class MessageSendSchema(MessageContentSchema):
    pass


class MessageCreateSchema(MessageSendSchema):
    chat_id: IDType
    sender_id: IDType


class MessageReadSchema(MessageIDSchema, MessageTimestampSchema, MessageCreateSchema):
    pass


class MessageDeleteSchema(MessageIDSchema):
    pass


class MessageEditSchema(MessageIDSchema, MessageContentSchema):
    pass


class MessagePutAnnouncementSchema(Base):
    announcement_type = "message/put"
    message: MessageReadSchema


class MessageDeleteAnnouncementSchema(Base):
    announcement_type = "message/delete"
    message: MessageReadSchema


class MessageAttachmentsAnnouncementSchema(Base):
    announcement_type = "message/attachments"
    attachments: Sequence[AttachmentReadSchema]


class MessageFetchSchema(Base):
    chat_id: IDType
    since: datetime | None = None
    until: datetime | None = None
    count: int | None = None

    @model_validator(mode="after")
    def check(self) -> Self:
        if not any(
            [
                self.since or self.until,
                self.since and self.until and not self.count,
            ]
        ):
            raise ValueError("invalid arguments")
        return self
