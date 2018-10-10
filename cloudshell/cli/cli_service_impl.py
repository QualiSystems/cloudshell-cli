import re

from cloudshell.cli.cli_service import CliService
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.command_mode_helper import CommandModeHelper


class CommandModeContextManager(object):
    """
    Context manager used to enter specific command mode
    """

    def __init__(self, cli_service, command_mode, logger):
        """
        :param cli_service:
        :type cli_service: CliServiceImpl
        :param command_mode
        :type command_mode: CommandMode
        """

        self._cli_service = cli_service
        self._command_mode = command_mode
        self._logger = logger
        self._previous_mode = CommandModeHelper.determine_current_mode(
            cli_service.session, command_mode, logger)

    def __enter__(self):
        """
        :return:
        :rtype: CliServiceImpl
        """

        self._cli_service._change_mode(self._command_mode)
        return self._cli_service

    def __exit__(self, type, value, traceback):
        if type:  # if we catch an error throw it upper
            return False

        self._cli_service._change_mode(self._previous_mode)


class CliServiceImpl(CliService):
    """
    Session wrapper, used to keep session mode and enter any child mode
    """

    def __init__(self, session, requested_command_mode, logger):
        """

        :param session:
        :param requested_command_mode:
        :param logger:
        """
        super(CliServiceImpl, self).__init__(session, logger)
        self._initialize(requested_command_mode)

    def _initialize(self, requested_command_mode):
        """
        :type requested_command_mode: cloudshell.cli.command_mode.CommandMode
        """
        self.command_mode = CommandModeHelper.determine_current_mode(self.session, requested_command_mode, self._logger)
        self.command_mode.enter_actions(self)
        self.command_mode.prompt_actions(self, self._logger)
        self._change_mode(requested_command_mode)

    def enter_mode(self, command_mode):
        """
        Enter child mode
        :param command_mode:
        :type command_mode: CommandMode
        :return:
        :rtype: CommandModeContextManager
        """
        return CommandModeContextManager(self, command_mode, self._logger)

    def send_command(self, command, expected_string=None, action_map=None, error_map=None, logger=None,
                     remove_prompt=False, *args, **kwargs):
        """
        Send command
        :param command:
        :param expected_string:
        :param action_map:
        :param error_map:
        :param logger:
        :param remove_prompt:
        :param args:
        :param kwargs:
        :return: Command output
        :rtype: str
        """
        if not expected_string:
            expected_string = self.command_mode.prompt

        if not logger:
            logger = self._logger
        self.session.logger = logger
        output = self.session.hardware_expect(command, expected_string=expected_string, action_map=action_map,
                                              error_map=error_map, logger=logger, *args, **kwargs)
        if remove_prompt:
            output = re.sub(r'^.*{}.*$'.format(expected_string), '', output, flags=re.MULTILINE)
        return output

    def _change_mode(self, requested_command_mode):
        """
        Change command mode
        :param requested_command_mode:
        :type requested_command_mode: CommandMode
        """
        if requested_command_mode:
            steps = CommandModeHelper.calculate_route_steps(self.command_mode, requested_command_mode)
            map(lambda x: x(self, self._logger), steps)

    def reconnect(self, timeout=None):
        """
        Reconnect session, keep current command mode
        :param timeout: Timeout for operation
        :return:
        """
        prompts_re = r'|'.join(CommandModeHelper.defined_modes_by_prompt(self.command_mode).keys())
        self.session.reconnect(prompts_re, self._logger, timeout)
        self._initialize(self.command_mode)
