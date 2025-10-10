from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, PrimaryKeyIDMixin

if TYPE_CHECKING:
    from . import ChatModel


class UserModel(Base, PrimaryKeyIDMixin):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(unique=True)
    fullname: Mapped[str] = mapped_column(String(50))
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str]

    chats: Mapped[list[ChatModel]] = relationship(
        "ChatModel",
        secondary="chat_user",
        back_populates="users",
    )
