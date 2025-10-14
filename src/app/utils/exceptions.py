from collections.abc import Mapping

from starlette.datastructures import Address
from starlette.exceptions import HTTPException

from app.schemas import UserIDSchema


class ContextRequiredToAccessAttributeError(PermissionError):
    def __init__(self, property_name: str, *args) -> None:
        super().__init__(
            f"Context required to access attribute {property_name}",
            *args,
        )


class TokenValidationError(HTTPException):
    def __init__(self, *, headers: Mapping[str, str] | None = None) -> None:
        super().__init__(401, "Unauthorized", headers)


class PasswordVerificationError(BaseException):
    def __init__(self) -> None:
        super().__init__("Password hash mismatch")


class InstantiationNotAllowedError(BaseException):
    def __init__(self, name: str) -> None:
        super().__init__(f"Cannot instantiate {name}")


class WebSocketUserNotConnectedError(HTTPException):
    def __init__(
        self, *, user: UserIDSchema, headers: Mapping[str, str] | None = None
    ) -> None:
        super().__init__(403, f"{user.id} is not in th connection pool", headers)


class WebSocketClientAlreadyConnected(HTTPException):
    def __init__(
        self,
        *,
        user: UserIDSchema,
        client: Address,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(
            403,
            f"{user.id}, client {client} is already in the connection pool",
            headers,
        )


class WebSocketNoClientError(HTTPException):
    def __init__(
        self, *, user: UserIDSchema, headers: Mapping[str, str] | None = None
    ) -> None:
        super().__init__(
            403, f"{user.id} no client associated with websocket connection", headers
        )
