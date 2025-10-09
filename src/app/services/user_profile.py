from app.schemas import (
    UserFullNameSchema,
    UserIDSchema,
    UserReadSchema,
    UserUserNameSchema,
)

from . import BaseService
from .exceptions import UserNotFoundError


class UserProfileService(BaseService):
    async def get_user(self, *, idSchema: UserIDSchema) -> UserReadSchema:
        async with self.uow as uow:
            user = await uow.userRepository.get(idSchema)
            if not user:
                raise UserNotFoundError
            return UserReadSchema.model_validate(user)

    async def edit_username(
        self, *, idSchema: UserIDSchema, new_username: UserUserNameSchema
    ) -> None:
        async with self.uow as uow:
            user = await uow.userRepository.get(idSchema)
            if not user:
                raise UserNotFoundError
            await uow.userRepository.update_one(idSchema, username=new_username)
            await uow.commit()

    async def edit_fullname(
        self, *, idSchema: UserIDSchema, new_fullname: UserFullNameSchema
    ) -> None:
        async with self.uow as uow:
            user = await uow.userRepository.get(idSchema)
            if not user:
                raise UserNotFoundError
            await uow.userRepository.update_one(idSchema, fullname=new_fullname)
            await uow.commit()
