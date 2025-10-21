from collections.abc import Sequence
from datetime import datetime

from fastapi.datastructures import URL
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


class PresignedAttachmentsReadSchema(Base):
    allowed_method = "put"
    urls: Sequence[HttpUrl | URL | str]
    attachments: Sequence[AttachmentReadSchema]
