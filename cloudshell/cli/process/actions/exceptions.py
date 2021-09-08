from cloudshell.cli.process.exceptions import SessionProcessingException


class ActionsException(SessionProcessingException):
    pass


class ActionsReturnData(ActionsException):
    pass


class SessionLoopDetectorException(SessionProcessingException):
    pass
