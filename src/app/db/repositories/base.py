from collections.abc import Sequence
from operator import and_
from typing import Any

from pydantic import BaseModel
from sqlalchemy import (
    ColumnExpressionArgument,
    Result,
    Row,
    delete,
    func,
    select,
    update,
)
from sqlalchemy.orm.interfaces import ORMOption
from sqlalchemy.sql.elements import SQLCoreOperations

from app.db.models import PrimaryKeyID, PrimaryKeyIDMixin
from app.interfaces.db.repositories import AbstractGenericRepository
from app.schemas import IDSchema
from app.utils.types import TCCA


class GenericRepository[T_model: PrimaryKeyIDMixin, T_ID: IDSchema, T_add: BaseModel](
    AbstractGenericRepository[T_model, T_ID, T_add]
):
    model_cls: type[T_model]

    def __init_subclass__(cls, model: type[T_model], **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls.model_cls = model

    async def get(
        self, idSchema: IDSchema, options: Sequence[ORMOption] | None = None
    ) -> T_model | None:
        return await self._session.get(self.model_cls, idSchema.id, options=options)

    async def add_one(self, entity: T_add) -> T_model:
        obj = self.model_cls(**entity.model_dump())
        self._session.add(obj)
        return obj

    async def update_one(self, idSchema: T_ID, *args, **kwargs) -> None:
        stmt = (
            update(self.model_cls)
            .where(self.model_cls.id == idSchema.id)
            .values(*args, **kwargs)
        )
        await self._session.execute(stmt)

    async def delete_one(self, idSchema: T_ID) -> None:
        stmt = delete(self.model_cls).where(self.model_cls.id == idSchema.id)
        await self._session.execute(stmt)

    async def filter_one_by(self, clause: ColumnExpressionArgument[bool]) -> Any | None:
        result = await self.filter_by(clause)
        return result.scalar_one_or_none()

    async def filter_by(self, clause: ColumnExpressionArgument[bool]) -> Result[Any]:
        stmt = select(self.model_cls).where(clause)
        result = await self._session.execute(stmt)
        return result

    async def get_column_scalars[T_co_1, T_co_2, T_co_f](
        self,
        id_attr: TCCA[PrimaryKeyID],
        attrs: tuple[TCCA[T_co_1], TCCA[T_co_2]],
        filter_by: SQLCoreOperations[T_co_f],
        skip_id: IDSchema,
        contains: str | None = None,
        count: int | None = None,
    ) -> Sequence[Row[tuple[PrimaryKeyID, T_co_1, T_co_2]]]:
        stmt = select(id_attr, *attrs)

        if contains:
            stmt = stmt.where(
                and_(
                    func.lower(filter_by).contains(contains, autoescape=True),
                    id_attr != skip_id.id,
                )
            )
        if count:
            stmt = stmt.limit(count)

        result = await self._session.execute(stmt)
        return result.all()
