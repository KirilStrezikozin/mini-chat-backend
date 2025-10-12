from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from sqlalchemy import ColumnExpressionArgument, Result, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import ORMOption
from sqlalchemy.sql.elements import SQLCoreOperations

from app.db.models import PrimaryKeyID
from app.schemas import IDSchema
from app.utils.types import TCCA


class AbstractGenericRepository[T_model, T_ID: IDSchema, T_add](ABC):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    async def get(
        self, idSchema: T_ID, options: Sequence[ORMOption] | None = None
    ) -> T_model | None: ...

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
    async def get_column_scalars[T_co_1, T_co_2, T_co_f](
        self,
        id_attr: TCCA[PrimaryKeyID],
        attrs: tuple[TCCA[T_co_1], TCCA[T_co_2]],
        filter_by: SQLCoreOperations[T_co_f],
        skip_id: IDSchema,
        contains: str | None = None,
        count: int | None = None,
    ) -> Sequence[Row[tuple[PrimaryKeyID, T_co_1, T_co_2]]]: ...
