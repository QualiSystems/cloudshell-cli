from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.cli_operations import CliOperations


class CommandModeContextManager(object):
    """
    Context manager used to enter specific command mode
    """

    def __init__(self, cli_operations, command_mode, logger):
        """
        :param cli_operations:
        :type cli_operations: CliOperations
        :param command_mode
        :type command_mode: CommandMode
        """
        self._cli_operations = cli_operations
        self._command_mode = command_mode
        self._logger = logger
        self._previous_mode = None

    def __enter__(self):
        """
        :return:
        :rtype: CliOperations
        """
        self._command_mode.step_up(self._cli_operations)
        return self._cli_operations

    def __exit__(self, type, value, traceback):
        self._command_mode.step_down(self._cli_operations)


class CliOperationsImpl(CliOperations):
    """
    Session wrapper, used to keep session mode and enter any child mode
    """

    def __init__(self, session, command_mode, logger):
        """
                :param session:
                :param logger:
                :param command_mode:
                :return:
                """
        super(CliOperationsImpl, self).__init__()
        self.session = session
        self._logger = logger
        self.command_mode = CommandModeHelper.determine_current_mode(self.session, command_mode, self._logger)
        self.command_mode.enter_actions(self)
        self._change_mode(command_mode)

    def enter_mode(self, command_mode):
        """
        Enter child mode
        :param command_mode:
        :type command_mode: CommandMode
        :return:
        :rtype: CommandModeContextManager
        """
        return CommandModeContextManager(self, command_mode, self._logger)

    def send_command(self, command, expected_string=None, logger=None, *args, **kwargs):
        """
        Send command
        :param command:
        :type command: str
        :param expected_string:
        :type expected_string: str
        :param logger:
        :type logger: Logger
        :param args:
        :param kwargs:
        :return:
        """
        if not expected_string:
            expected_string = self.command_mode.prompt

        if not logger:
            logger = self._logger
        self.session.logger = logger
        return self.session.hardware_expect(command, expected_string=expected_string, logger=logger, *args,
                                            **kwargs)

    def _change_mode(self, new_command_mode):
        """
        Change command mode
        :param new_command_mode:
        :type new_command_mode: CommandMode
        """
        if new_command_mode:
            steps = CommandModeHelper.calculate_route_steps(self.command_mode, new_command_mode)
            map(lambda x: x(self), steps)
