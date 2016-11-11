class SessionException(Exception):
    pass


class ExpectedSessionException(SessionException):
    pass


class SessionLoopLimitException(ExpectedSessionException):
    pass


class SessionLoopDetectorException(ExpectedSessionException):
    pass


class CommandExecutionException(ExpectedSessionException):
    pass


class SessionReadTimeout(SessionException):
    pass


class SessionReadEmptyData(SessionException):
    pass
