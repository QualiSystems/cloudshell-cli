from cloudshell.cli.process.command.exception import SessionProcessingException


class ActionsException(SessionProcessingException):
    pass


class ActionsReturnData(ActionsException):
    pass


class SessionLoopDetectorException(SessionProcessingException):
    pass
