import uuid
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")
Factory = Callable[[], T]

IDType = uuid.UUID
