from cloudshell.cli.session.session import Session
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.session_mode_wrapper import SessionModeWrapper


class CommandModeContextManager(object):
    """
    Enter to specific command mode
    """
    def __init__(self, session, command_mode):
        """
        :param session:
        :type session: Session
        :param command_mode
        :type command_mode: CommandMode
        """
        self._session = session
        self._command_mode = command_mode

    def __enter__(self):
        """
        :return:
        :rtype: SessionModeWrapper
        """
        self._command_mode.step_up(self._session)
        return self._session

    def __exit__(self, type, value, traceback):
        self._command_mode.step_down(self._session)
