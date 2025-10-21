from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from typing import Any

from sqlalchemy import ColumnExpressionArgument, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import ORMOption

from app.schemas import IDSchema


class AbstractGenericRepository[T_model, T_ID: IDSchema, T_add](ABC):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    async def get(
        self, id_schema: T_ID, options: Sequence[ORMOption] | None = None
    ) -> T_model | None: ...

    @abstractmethod
    async def add_one(self, entity: T_add) -> T_model: ...

    @abstractmethod
    async def add_many(self, entities: Iterable[T_add]) -> list[T_model]: ...

    @abstractmethod
    async def update_one(
        self, id_schema: T_ID, returning: type[T_model], *args, **kwargs
    ) -> T_model: ...

    @abstractmethod
    async def delete_one(self, id_schema: T_ID) -> None: ...

    @abstractmethod
    async def filter_one_by(self, *clause: ColumnExpressionArgument) -> Any | None: ...

    @abstractmethod
    async def filter_by(self, *clause: ColumnExpressionArgument) -> Result[Any]: ...
