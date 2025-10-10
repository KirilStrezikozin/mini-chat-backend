from sqlalchemy.orm import Mapped

from .mappings import PrimaryKeyID, Timestamp


class PrimaryKeyIDMixin:
    id: Mapped[PrimaryKeyID]


class TimestampMixin:
    timestamp: Mapped[Timestamp]
