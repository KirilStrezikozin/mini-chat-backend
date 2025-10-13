class UserNameNotFoundError(BaseException):
    def __init__(
        self, *args: object, detail: str = "User with this username not found"
    ) -> None:
        self.detail = detail
        super().__init__(*args)


class UserEmailNotFoundError(BaseException):
    def __init__(
        self, *args: object, detail: str = "User with this email not found"
    ) -> None:
        self.detail = detail
        super().__init__(*args)


class UserNotFoundError(BaseException):
    def __init__(self, *args: object, detail: str = "User not found") -> None:
        self.detail = detail
        super().__init__(*args)


class ChatNotFoundError(BaseException):
    def __init__(self, *args: object, detail: str = "Chat not found") -> None:
        self.detail = detail
        super().__init__(*args)


class InalidChatUserID(BaseException):
    def __init__(self, *args: object, detail: str) -> None:
        self.detail = detail
        super().__init__(detail, *args)


class MessageNotFoundError(BaseException):
    def __init__(
        self, *args: object, detail: str = "Requested message not found"
    ) -> None:
        self.detail = detail
        super().__init__(*args)


class AttachmentNotFoundError(BaseException):
    def __init__(
        self, *args: object, detail: str = "Requested attachment not found"
    ) -> None:
        self.detail = detail
        super().__init__(*args)


class UserEmailAlreadyRegistered(BaseException):
    def __init__(
        self, *args: object, detail: str = "A user with this email already exists"
    ) -> None:
        self.detail = detail
        super().__init__(*args)


class UserNameAlreadyRegistered(BaseException):
    def __init__(
        self, *args: object, detail: str = "A user with this username already exists"
    ) -> None:
        self.detail = detail
        super().__init__(*args)


class UserNameMustStartWithAtSign(BaseException):
    def __init__(
        self, *args: object, detail: str = "Username must start with @ (at) sign"
    ) -> None:
        self.detail = detail
        super().__init__(*args)
