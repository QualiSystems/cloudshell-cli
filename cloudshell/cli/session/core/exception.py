class SessionException(Exception):
    pass


class SessionReadTimeout(SessionException):
    pass


class SessionReadEmptyData(SessionException):
    pass


class SessionFactoryException(SessionException):
    pass
