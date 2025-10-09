from typing import Any

from app.db.repositories import UserRepository
from app.schemas import (
    AccessTokenSchema,
    RefreshTokenSchema,
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
    UserNotFoundError,
)


class UserAuthService(BaseService):
    async def token(self, *, accessScheme: AccessTokenSchema) -> None:
        JWTManager.validate_token(self.config, accessScheme.access_token, "access")

    async def refresh_token(self, *, refreshSchema: RefreshTokenSchema) -> TokenSchema:
        payload = JWTManager.validate_token(
            self.config, refreshSchema.refresh_token, "refresh"
        )

        idSchema = UserIDSchema(id=payload.id)

        async with self.uow as uow:
            user = await uow.userRepository.get(idSchema)
            if not user:
                raise UserNotFoundError

        return JWTManager.create_token_schema(self.config, idSchema)

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

    async def register(self, registerSchema: UserRegisterSchema) -> TokenSchema:
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
