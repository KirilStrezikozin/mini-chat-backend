from sqlalchemy.exc import IntegrityError

from app.core.exceptions import UserNameAlreadyRegistered
from app.db.models import UserModel
from app.schemas import (
    UserFullNameSchema,
    UserIDSchema,
    UserProfileSchema,
    UserReadSchema,
    UserUserNameSchema,
)

from .base import BaseService


class UserProfileService(BaseService):
    async def get_user_profile(self, *, user_schema: UserIDSchema) -> UserProfileSchema:
        async with self.uow as uow:
            user_resource = await self._get_user_resource(uow, user_schema)
            user = UserReadSchema.model_validate(user_resource)
            return UserProfileSchema(**user.model_dump())

    async def _patch(
        self, user_schema: UserIDSchema, **patch_kwargs
    ) -> UserProfileSchema:
        async with self.uow as uow:
            # Ensure the requested user exists.
            _ = await self._get_user_resource(uow, user_schema)
            user_resource = await uow.userRepository.update_one(
                user_schema, UserModel, **patch_kwargs
            )
            user = UserReadSchema.model_validate(user_resource)
            return UserProfileSchema(**user.model_dump())

    async def patch_username(
        self, *, user_schema: UserIDSchema, username_schema: UserUserNameSchema
    ) -> UserProfileSchema:
        try:
            return await self._patch(user_schema, username=username_schema.username)
        except IntegrityError as error:
            raise UserNameAlreadyRegistered from error

    async def patch_fullname(
        self, *, user_schema: UserIDSchema, fullname_schema: UserFullNameSchema
    ) -> UserProfileSchema:
        return await self._patch(user_schema, fullname=fullname_schema.fullname)
