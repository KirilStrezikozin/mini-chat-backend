from datetime import datetime
from typing import Annotated, Self

from pydantic import BaseModel, StringConstraints, model_validator

from app.utils.types import IDType

from . import IDSchema


class MessageIDSchema(IDSchema):
    pass


class MessageContentSchema(BaseModel):
    content: Annotated[str, StringConstraints(max_length=5000)]


class MessageTimestampSchema(BaseModel):
    timestamp: datetime


class MessageCreateSchema(MessageContentSchema, MessageTimestampSchema):
    sender_id: IDType
    chat_id: IDType


class MessageReadSchema(MessageIDSchema, MessageCreateSchema):
    pass


class MessageDeleteSchema(MessageIDSchema):
    pass


class MessageChangeContentSchema(MessageIDSchema, MessageContentSchema):
    pass


class MessageFetchSchema(BaseModel):
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
