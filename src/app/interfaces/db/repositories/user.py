from abc import abstractmethod
from collections.abc import Sequence

from sqlalchemy import Row

from app.db.models import PrimaryKeyID, UserModel
from app.schemas import (
    ChatSearchByType,
    UserCreateSchema,
    UserIDSchema,
)

from .base import AbstractGenericRepository


class AbstractUserRepository(
    AbstractGenericRepository[UserModel, UserIDSchema, UserCreateSchema],
):
    @abstractmethod
    async def search_by(
        self,
        contains: str,
        by: ChatSearchByType,
        skip_id: UserIDSchema,
        count: int | None = None,
    ) -> Sequence[Row[tuple[PrimaryKeyID, str, str]]]: ...
