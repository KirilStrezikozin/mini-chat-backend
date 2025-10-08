from app.db.models.user import UserModel
from app.schemas.user import (
    UserCreateSchema,
    UserIDSchema,
)

from . import AbstractGenericRepository


class AbstractUserRepository(
    AbstractGenericRepository[UserModel, UserIDSchema, UserCreateSchema],
):
    pass
