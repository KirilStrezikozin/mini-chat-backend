class ContextRequiredToAccessAttributeError(PermissionError):
    def __init__(self, property_name: str, *args) -> None:
        super().__init__(
            f"Context required to access attribute {property_name}",
            *args,
        )


class TokenValidationError(BaseException):
    pass


class PasswordVerificationError(BaseException):
    def __init__(self) -> None:
        super().__init__("Password hash mismatch")


class InstantiationNotAllowedError(BaseException):
    def __init__(self, name: str) -> None:
        super().__init__(f"Cannot instantiate {name}")


class ClientNotConnectedError(BaseException):
    def __init__(self, id: str) -> None:
        super().__init__(f"WebSocket client with id={id} is not in the connection pool")


class WebSocketClientAlreadyConnected(BaseException):
    def __init__(self, id: str) -> None:
        super().__init__(
            f"WebSocket client with id={id} is already in the connection pool"
        )
