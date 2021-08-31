class SessionProcessingException(Exception):
    pass


class SessionLoopLimitException(SessionProcessingException):
    pass


class CommandExecutionException(SessionProcessingException):
    pass
