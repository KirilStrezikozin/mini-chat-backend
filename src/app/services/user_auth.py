from app.core.exceptions import (
    LoginError,
    PasswordVerificationError,
    UserEmailAlreadyRegistered,
    UserNameAlreadyRegistered,
)
from app.db.repositories import UserRepository
from app.schemas import (
    TokenSchema,
    UserCreateSchema,
    UserIDSchema,
    UserLoginSchema,
    UserPasswordSchema,
    UserReadSchema,
    UserRegisterSchema,
)
from app.utils.security import JWTManager, PasswordManager

from .base import BaseService


class UserAuthService(BaseService):
    async def login(self, *, login_schema: UserLoginSchema) -> TokenSchema:
        async with self.uow as uow:
            model = UserRepository.model_cls

            user_resource = await uow.userRepository.filter_one_by(
                (model.username == login_schema.username)
                if login_schema.username
                else (model.email == login_schema.email)
            )

            if not user_resource:
                raise LoginError

            user = UserReadSchema.model_validate(user_resource)

        try:
            PasswordManager.verify_password(login_schema.password, user.password_hash)
        except PasswordVerificationError as error:
            raise LoginError from error

        return JWTManager.create_token_schema(self.config, UserIDSchema(id=user.id))

    async def register(self, *, register_schema: UserRegisterSchema) -> TokenSchema:
        password_hash = PasswordManager.get_password_hash(register_schema.password)

        user_schema = UserCreateSchema(
            fullname=register_schema.fullname,
            username=register_schema.username,
            email=register_schema.email,
            password_hash=password_hash,
        )

        async with self.uow as uow:
            if await uow.userRepository.filter_one_by(
                UserRepository.model_cls.username == user_schema.username
            ):
                raise UserNameAlreadyRegistered

            if await uow.userRepository.filter_one_by(
                UserRepository.model_cls.email == user_schema.email
            ):
                raise UserEmailAlreadyRegistered

            user_resource = await uow.userRepository.add_one(user_schema)
            user = UserReadSchema.model_validate(user_resource)

        return JWTManager.create_token_schema(self.config, UserIDSchema(id=user.id))

    async def delete_user_account(
        self, *, user_schema: UserIDSchema, password_schema: UserPasswordSchema
    ) -> None:
        async with self.uow as uow:
            user_resource = await self._get_user_resource(uow, user_schema)
            user = UserReadSchema.model_validate(user_resource)

            PasswordManager.verify_password(
                password_schema.password, user.password_hash
            )

            await uow.userRepository.delete_one(user_schema)
