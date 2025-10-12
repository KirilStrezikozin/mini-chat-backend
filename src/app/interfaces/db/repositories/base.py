from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from sqlalchemy import ColumnExpressionArgument, Result, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import SQLCoreOperations

from app.schemas import IDSchema
from app.utils.types import TCCA


class AbstractGenericRepository[T_model, T_ID: IDSchema, T_add](ABC):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    async def get(self, idSchema: T_ID) -> T_model | None: ...

    @abstractmethod
    async def add_one(self, entity: T_add) -> T_model: ...

    @abstractmethod
    async def update_one(self, idSchema: T_ID, *args, **kwargs) -> None: ...

    @abstractmethod
    async def delete_one(self, idSchema: T_ID) -> None: ...

    @abstractmethod
    async def filter_one_by(self, clause: ColumnExpressionArgument) -> Any | None: ...

    @abstractmethod
    async def filter_by(self, clause: ColumnExpressionArgument) -> Result[Any]: ...

    @abstractmethod
    async def get_column_scalars[T_co_0, T_co_1, T_co_2, T_co_f](
        self,
        attr: tuple[TCCA[T_co_0], TCCA[T_co_1], TCCA[T_co_2]],
        filter_by: SQLCoreOperations[T_co_f],
        contains: str | None = None,
        count: int | None = None,
    ) -> Sequence[Row[tuple[T_co_0, T_co_1, T_co_2]]]: ...
