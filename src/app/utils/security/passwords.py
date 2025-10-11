import bcrypt

from app.utils.exceptions import (
    InstantiationNotAllowedError,
    PasswordVerificationError,
)


class PasswordManager:
    def __init__(self) -> None:
        raise InstantiationNotAllowedError(self.__class__.__name__)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> None:
        if not bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        ):
            raise PasswordVerificationError

    @staticmethod
    def get_password_hash(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
