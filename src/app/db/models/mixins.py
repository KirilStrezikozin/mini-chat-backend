from sqlalchemy.orm import Mapped

from . import PrimaryKeyID, Timestamp


class PrimaryKeyIDMixin:
    id: Mapped[PrimaryKeyID]


class TimestampMixin:
    timestamp: Mapped[Timestamp]
