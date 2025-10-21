from sqlalchemy import func, select

from app.db.models import UserModel
from app.db.repositories import GenericRepository
from app.interfaces.db.repositories import AbstractUserRepository
from app.schemas import (
    ChatSearchByType,
    UserCreateSchema,
    UserIDSchema,
)


class UserRepository(
    AbstractUserRepository,
    GenericRepository[UserModel, UserIDSchema, UserCreateSchema],
    model=UserModel,
):
    async def search_by(
        self,
        contains: str,
        by: ChatSearchByType,
        skip_id: UserIDSchema,
        count: int | None = None,
    ):
        filter_by = (
            self.model_cls.fullname
            if by.value == "fullname"
            else self.model_cls.username
        )

        stmt = (
            select(self.model_cls.id, self.model_cls.fullname, self.model_cls.username)
            .where(
                self.model_cls.id != skip_id.id,
                func.lower(filter_by).contains(contains.lower(), autoescape=True),
            )
            .limit(count)
        )

        result = await self._session.execute(stmt)
        return result.all()
