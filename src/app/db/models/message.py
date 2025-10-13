from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.types import IDType

from .attachment import AttachmentModel
from .base import Base
from .mixins import PrimaryKeyIDMixin, TimestampMixin
from .user import UserModel

if TYPE_CHECKING:
    from . import ChatModel


class MessageModel(Base, PrimaryKeyIDMixin, TimestampMixin):
    __tablename__ = "message"

    content: Mapped[str] = mapped_column(String(5000))
    sender_id: Mapped[IDType] = mapped_column(ForeignKey("user.id"))
    chat_id: Mapped[IDType] = mapped_column(ForeignKey("chat.id"))

    chat: Mapped["ChatModel"] = relationship(
        "ChatModel",
        foreign_keys=[chat_id],
        back_populates="messages",
    )

    sender: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[sender_id],
    )

    attachments: Mapped[list["AttachmentModel"]] = relationship(
        "AttachmentModel",
        back_populates="message",
        cascade="all, delete-orphan",
    )
