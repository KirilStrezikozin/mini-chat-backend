from fastapi import HTTPException, WebSocketException, status


def _make_not_found_error(resource_name: str):
    resource = resource_name.capitalize()

    class NotFoundError(HTTPException):
        def __init__(self) -> None:
            super().__init__(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{resource} not found",
            )

    NotFoundError.__name__ = f"{resource}NotFoundError"
    return NotFoundError


UserNotFoundError = _make_not_found_error("user")
ChatNotFoundError = _make_not_found_error("chat")
MessageNotFoundError = _make_not_found_error("message")
AttachmentNotFoundError = _make_not_found_error("attachment")


class UserEmailAlreadyRegistered(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )


class UserNameAlreadyRegistered(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this username already exists",
        )


class LoginError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username, email, or password is incorrect",
        )


class TokenValidationError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )


class PasswordVerificationError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )


class InstantiationNotAllowedError(BaseException):
    def __init__(self, name: str) -> None:
        super().__init__(f"Cannot instantiate {name}")


class WebSocketNoClientError(WebSocketException):
    def __init__(self) -> None:
        super().__init__(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="No client associated with websocket connection",
        )
