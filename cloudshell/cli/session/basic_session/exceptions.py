class SessionException(Exception):
    pass


class SessionReadTimeout(SessionException):
    pass


class SessionReadEmptyData(SessionException):
    pass


class PromCannotBeDefinedException(SessionException):
    pass
