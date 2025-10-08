from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel
from sqlalchemy import ColumnExpressionArgument, Result, delete, select, update
from sqlalchemy.sql.elements import SQLCoreOperations

from app.db.models import PrimaryKeyIDMixin
from app.interfaces.db.repositories import AbstractGenericRepository
from app.schemas import IDSchema


class GenericRepository[T_model: PrimaryKeyIDMixin, T_ID: IDSchema, T_add: BaseModel](
    AbstractGenericRepository[T_model, T_ID, T_add]
):
    model_cls: type[T_model]

    def __init_subclass__(cls, model: type[T_model], **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls.model_cls = model

    async def get(self, idSchema: IDSchema) -> T_model | None:
        return await self._session.get(self.model_cls, idSchema.id)

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

    async def get_column_scalars[T_co](
        self,
        attr: SQLCoreOperations[T_co],
        contains: str | None = None,
        count: int | None = None,
    ) -> Sequence[T_co]:
        stmt = select(attr)

        if contains:
            stmt = stmt.where(attr.contains(contains, autoescape=True))
        if count:
            stmt = stmt.limit(count)

        result = await self._session.execute(stmt)
        return result.scalars().all()
