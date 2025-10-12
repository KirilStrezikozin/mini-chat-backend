import uuid
from collections.abc import Callable
from typing import TypeVar, Union

from sqlalchemy.sql import roles
from sqlalchemy.sql.elements import SQLCoreOperations

T = TypeVar("T")
Factory = Callable[[], T]

IDType = uuid.UUID

TCCA = Union[
    roles.TypedColumnsClauseRole[T],
    "SQLCoreOperations[T]",
    type[T],
]
