from datetime import datetime
from typing import Literal

from pydantic import HttpUrl

from app.utils.types import IDType

from .base import Base, IDSchema


class AttachmentIDSchema(IDSchema):
    pass


class AttachmentCreateSchema(Base):
    content_type: str
    filename: str
    message_id: IDType


class AttachmentReadSchema(AttachmentIDSchema, AttachmentCreateSchema):
    timestamp: datetime


class PresignedAttachmentReadSchema(Base):
    url: HttpUrl
    allowed_method: Literal["put", "get"]
    attachment: AttachmentReadSchema
