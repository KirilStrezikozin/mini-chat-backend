class UserNameNotFoundError(BaseException):
    pass


class UserEmailNotFoundError(BaseException):
    pass


class UserNotFoundError(BaseException):
    pass


class ChatNotFoundError(BaseException):
    pass


class MessageNotFoundError(BaseException):
    pass


class UserEmailAlreadyRegistered(BaseException):
    pass


class UserNameAlreadyRegistered(BaseException):
    pass


class UserNameMustStartWithAtSign(BaseException):
    pass
