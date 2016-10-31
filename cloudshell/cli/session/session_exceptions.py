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
