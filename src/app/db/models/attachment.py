from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.types import IDType

from .base import Base
from .mixins import PrimaryKeyIDMixin, TimestampMixin

if TYPE_CHECKING:
    from . import MessageModel


class AttachmentModel(Base, PrimaryKeyIDMixin, TimestampMixin):
    __tablename__ = "attachment"

    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(255))

    message_id: Mapped[IDType] = mapped_column(
        ForeignKey("message.id", ondelete="CASCADE")
    )

    message: Mapped["MessageModel"] = relationship(
        "MessageModel",
        back_populates="attachments",
    )
