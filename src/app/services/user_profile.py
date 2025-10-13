from sqlalchemy.exc import IntegrityError

from app.schemas import (
    UserFullNameSchema,
    UserIDSchema,
    UserProfileSchema,
    UserReadSchema,
    UserUserNameSchema,
)

from .base import BaseService
from .exceptions import UserNameAlreadyRegistered, UserNotFoundError


class UserProfileService(BaseService):
    async def get_user(self, *, idSchema: UserIDSchema) -> UserProfileSchema:
        async with self.uow as uow:
            resource = await uow.userRepository.get(idSchema)
            if not resource:
                raise UserNotFoundError
            user = UserReadSchema.model_validate(resource)
            return UserProfileSchema(
                username=user.username,
                fullname=user.fullname,
                email=user.email,
            )

    async def edit_username(
        self, *, idSchema: UserIDSchema, new_username_schema: UserUserNameSchema
    ) -> None:
        async with self.uow as uow:
            user = await uow.userRepository.get(idSchema)
            if not user:
                raise UserNotFoundError

            try:
                await uow.userRepository.update_one(
                    idSchema, username=new_username_schema.username
                )
            except IntegrityError as error:
                raise UserNameAlreadyRegistered from error

            await uow.commit()

    async def edit_fullname(
        self, *, idSchema: UserIDSchema, new_fullname_schema: UserFullNameSchema
    ) -> None:
        async with self.uow as uow:
            user = await uow.userRepository.get(idSchema)
            if not user:
                raise UserNotFoundError

            await uow.userRepository.update_one(
                idSchema, fullname=new_fullname_schema.fullname
            )

            await uow.commit()
