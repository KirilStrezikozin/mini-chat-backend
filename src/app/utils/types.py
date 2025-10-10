import uuid
from collections.abc import Callable
from typing import Literal, TypeVar

T = TypeVar("T")
Factory = Callable[[], T]

TokenType = Literal["access", "refresh"]

IDType = uuid.UUID
