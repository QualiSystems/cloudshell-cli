from cloudshell.cli.session.session import Session
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.command_mode_context_manager import CommandModeContextManager


class CommandModeSessionWrapper(object):
    """
    Keep session state wrapper
    """
    def __init__(self, session, command_mode):
        """
        :param session:
        :type session: Session
        :param command_mode:
        :type command_mode: CommandMode
        :return:
        """

        self._session = session
        self._command_mode = command_mode

    def __getattr__(self, name):
        attr = getattr(self._instance, name)
        return attr

    @property
    def command_mode(self):
        return self._command_mode

    @command_mode.setter
    def command_mode(self, command_mode):
        """
        :param command_mode:
        :type command_mode: CommandMode
        """
        self._command_mode = command_mode

    def enter_mode(self, command_mode):
        """
        Enter specific mode
        :param command_mode:
        :type command_mode: CommandMode
        :return:
        :rtype: CommandModeContextManager
        """
        return CommandModeContextManager(self._session, command_mode)

    def send_command(self, command, expected_string=None, logger=None, *args, **kwargs):

        if not expected_string:
            expected_string = self._command_mode.promt

        self._session.logger = logger
        self._session.hardware_expect(command, expected_string=expected_string, *args, **kwargs)
