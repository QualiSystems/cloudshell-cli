from cloudshell.cli.session.session import Session
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.cli_operations import CLIOperations


class CommandModeContextManager(object):
    """
    Enter to specific command mode
    """

    def __init__(self, session, command_mode, logger):
        """
        :param session:
        :type session: CommandModeSessionWrapper
        :param command_mode
        :type command_mode: CommandMode
        """
        self._session = session
        self._command_mode = command_mode
        self._logger = logger
        self._previous_mode = None

    def __enter__(self):
        """
        :return:
        :rtype: CommandModeSessionWrapper
        """
        self._command_mode.step_up(self._session, logger=self._logger)
        self._previous_mode = self._session.command_mode
        self._session.command_mode = self._command_mode
        return self._session

    def __exit__(self, type, value, traceback):
        self._command_mode.step_down(self._session, logger=self._logger)
        self._session.command_mode = self._previous_mode


class CommandModeSessionWrapper(CLIOperations):
    """
    Keep session state wrapper
    """

    def __init__(self, session, command_mode, logger):
        """
        :param session:
        :type session: Session
        :param command_mode:
        :type command_mode: CommandMode
        :return:
        """

        self._session = session
        self.command_mode = command_mode
        self._logger = logger

    def __getattr__(self, name):
        attr = getattr(self._session, name)
        return attr

    @property
    def session(self):
        return self._session

    # @property
    # def command_mode(self):
    #     """
    #
    #     :return:
    #     :rtype: CommandMode
    #     """
    #     return self._command_mode
    #
    # @command_mode.setter
    # def command_mode(self, command_mode):
    #     self._command_mode = command_mode

    def enter_mode(self, command_mode):
        """
        Enter specific mode
        :param command_mode:
        :type command_mode: CommandMode
        :return:
        :rtype: CommandModeContextManager
        """
        return CommandModeContextManager(self, command_mode, self._logger)

    def send_command(self, command, expected_string=None, logger=None, *args, **kwargs):
        if not expected_string:
            expected_string = self.command_mode.prompt

        self._session.logger = logger
        return self._session.hardware_expect(command, expected_string=expected_string, logger=logger, *args, **kwargs)
