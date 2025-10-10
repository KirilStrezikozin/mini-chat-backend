from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.types import IDType

from .base import Base
from .message import MessageModel
from .mixins import PrimaryKeyIDMixin
from .user import UserModel


class ChatModel(Base, PrimaryKeyIDMixin):
    __tablename__ = "chat"

    messages: Mapped[list["MessageModel"]] = relationship(
        "MessageModel",
        back_populates="chat",
        cascade="all, delete-orphan",
    )

    users: Mapped[list["UserModel"]] = relationship(
        "UserModel",
        secondary="chat_user",
        back_populates="chats",
    )


class ChatUserModel(Base):
    __tablename__ = "chat_user"

    chat_id: Mapped[IDType] = mapped_column(
        ForeignKey("chat.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user_id: Mapped[IDType] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )
