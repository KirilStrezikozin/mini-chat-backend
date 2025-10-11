from typing import Any

from app.db.repositories import UserRepository
from app.schemas import (
    TokenSchema,
    UserCreateSchema,
    UserIDSchema,
    UserLoginSchema,
    UserReadSchema,
    UserRegisterSchema,
)
from app.utils.security import JWTManager, PasswordManager

from . import BaseService
from .exceptions import (
    UserEmailAlreadyRegistered,
    UserEmailNotFoundError,
    UserNameAlreadyRegistered,
    UserNameNotFoundError,
)


class UserAuthService(BaseService):
    async def login(self, *, loginSchema: UserLoginSchema) -> TokenSchema:
        async with self.uow as uow:
            model = UserRepository.model_cls

            resource: Any
            if loginSchema.username:
                resource = await uow.userRepository.filter_one_by(
                    model.username == loginSchema.username
                )

                if not resource:
                    raise UserNameNotFoundError

            else:
                resource = await uow.userRepository.filter_one_by(
                    model.email == loginSchema.email
                )

                if not resource:
                    raise UserEmailNotFoundError

            user = UserReadSchema.model_validate(resource)

        PasswordManager.verify_password(loginSchema.password, user.password_hash)

        return JWTManager.create_token_schema(self.config, UserIDSchema(id=user.id))

    async def register(self, *, registerSchema: UserRegisterSchema) -> TokenSchema:
        password_hash = PasswordManager.get_password_hash(registerSchema.password)

        userSchema = UserCreateSchema(
            fullname=registerSchema.fullname,
            username=registerSchema.username,
            email=registerSchema.email,
            password_hash=password_hash,
        )

        async with self.uow as uow:
            if await uow.userRepository.filter_one_by(
                UserRepository.model_cls.username == userSchema.username
            ):
                raise UserNameAlreadyRegistered

            if await uow.userRepository.filter_one_by(
                UserRepository.model_cls.email == userSchema.email
            ):
                raise UserEmailAlreadyRegistered

            resource = await uow.userRepository.add_one(userSchema)
            await uow.commit()

            user = UserReadSchema.model_validate(resource)

        return JWTManager.create_token_schema(self.config, UserIDSchema(id=user.id))
