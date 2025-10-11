from typing import Annotated, Self

from pydantic import EmailStr, StringConstraints, model_validator

from . import Base, IDSchema

UserNameAnnotation = Annotated[
    str, StringConstraints(max_length=50, min_length=2, pattern=r"^@")
]


class UserIDSchema(IDSchema):
    pass


class UserFullNameSchema(Base):
    fullname: Annotated[str, StringConstraints(max_length=50)]


class UserUserNameSchema(Base):
    username: UserNameAnnotation


class UserProfileSchema(UserUserNameSchema, UserFullNameSchema):
    email: EmailStr


class UserCreateSchema(UserProfileSchema):
    password_hash: str


class UserReadSchema(UserIDSchema, UserCreateSchema):
    pass


class UserRegisterSchema(UserProfileSchema):
    password: str


class UserLoginSchema(Base):
    username: UserNameAnnotation | None = None
    email: EmailStr | None = None
    password: str

    @model_validator(mode="after")
    def check_identifier_present(self) -> Self:
        if (self.username is None) == (self.email is None):
            raise ValueError("either username or email must be set")
        return self


class UserDeleteSchema(UserIDSchema):
    pass


class UserChangeFullNameSchema(UserIDSchema, UserFullNameSchema):
    pass


class UserChangeUserNameSchema(UserIDSchema, UserUserNameSchema):
    pass
