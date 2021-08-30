class AdvancedSessionException(Exception):
    pass


class SessionLoopLimitException(AdvancedSessionException):
    pass


class SessionLoopDetectorException(AdvancedSessionException):
    pass


class CommandExecutionException(AdvancedSessionException):
    pass



