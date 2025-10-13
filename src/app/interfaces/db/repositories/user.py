from app.db.models.user import UserModel
from app.schemas.user import (
    UserCreateSchema,
    UserIDSchema,
)

from .base import AbstractGenericRepository


class AbstractUserRepository(
    AbstractGenericRepository[UserModel, UserIDSchema, UserCreateSchema],
):
    pass
