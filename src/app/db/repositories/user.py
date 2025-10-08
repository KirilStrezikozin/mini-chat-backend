from app.db.models import UserModel
from app.db.repositories import GenericRepository
from app.interfaces.db.repositories import AbstractUserRepository
from app.schemas import (
    UserCreateSchema,
    UserIDSchema,
)


class UserRepository(
    AbstractUserRepository,
    GenericRepository[UserModel, UserIDSchema, UserCreateSchema],
    model=UserModel,
):
    pass
