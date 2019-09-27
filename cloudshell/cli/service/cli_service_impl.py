import re

from cloudshell.cli.service.cli_service import CliService
from cloudshell.cli.service.command_mode_helper import CommandModeHelper


class EnterCommandModeContextManager(object):
    def __init__(self, cli_service, command_mode, logger):
        """Context manager used to enter specific command mode.

         These command modes using CommandMode relations
            in CommandMode.RELATIONS_DICT

        :param CliServiceImpl cli_service:
        :param CommandMode command_mode:
        :param logging.Logger logger:
        """
        self._cli_service = cli_service
        self._command_mode = command_mode
        self._logger = logger
        self._previous_mode = cli_service.command_mode

    def __enter__(self):
        """Enter.

        :rtype: CliServiceImpl
        """
        self._cli_service._change_mode(self._command_mode)
        return self._cli_service

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:  # if we catch an error throw it upper
            return False

        self._cli_service._change_mode(self._previous_mode)


class EnterDetachCommandModeContextManager(EnterCommandModeContextManager):
    def __init__(self, cli_service, command_mode, logger):
        """Context manager used to enter specific command mode.

        These command modes works without using CommandMode relations
        in CommandMode.RELATIONS_DICT
        """
        super(EnterDetachCommandModeContextManager, self).__init__(
            cli_service, command_mode, logger
        )

        if command_mode.parent_node is None:
            command_mode.parent_node = self._previous_mode

    def __enter__(self):
        """Enter.

        :rtype: CliServiceImpl
        """
        self._command_mode.step_up(self._cli_service, self._logger)
        return self._cli_service

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:  # if we catch an error throw it upper
            return False

        self._command_mode.step_down(self._cli_service, self._logger)


CommandModeContextManager = EnterDetachCommandModeContextManager  # Deprecated


class CliServiceImpl(CliService):
    """Session wrapper, used to keep session mode and enter any child mode."""

    def __init__(self, session, requested_command_mode, logger):
        super(CliServiceImpl, self).__init__(session, logger)
        self._initialize(requested_command_mode)

    def _initialize(self, requested_command_mode):
        """Initialize.

        :type requested_command_mode: cloudshell.cli.command_mode.CommandMode
        """
        self.command_mode = CommandModeHelper.determine_current_mode(
            self.session, requested_command_mode, self._logger
        )
        self.command_mode.enter_actions(self)
        self.command_mode.prompt_actions(self, self._logger)
        self._change_mode(requested_command_mode)

    def enter_mode(self, command_mode):
        """Enter specified command mode.

        :param command_mode:
        :type command_mode: CommandMode
        :return: context manager
        :rtype: EnterCommandModeContextManager|EnterDetachCommandModeContextManager
        """
        if command_mode.is_attached_command_mode():
            context = EnterCommandModeContextManager
        else:
            context = EnterDetachCommandModeContextManager

        return context(self, command_mode, self._logger)

    def send_command(
        self,
        command,
        expected_string=None,
        action_map=None,
        error_map=None,
        logger=None,
        remove_prompt=False,
        *args,
        **kwargs
    ):
        """Send command.

        :param command:
        :param expected_string:
        :param action_map:
        :param error_map: expected error map with subclass of CommandExecutionException
            or str
        :type error_map: dict[str, cloudshell.cli.session.session_exceptions.CommandExecutionException|str]  # noqa: E501
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
        output = self.session.hardware_expect(
            command,
            expected_string=expected_string,
            action_map=action_map,
            error_map=error_map,
            logger=logger,
            *args,
            **kwargs
        )
        if remove_prompt:
            output = re.sub(
                r"^.*{}.*$".format(expected_string), "", output, flags=re.MULTILINE
            )
        return output

    def _change_mode(self, requested_command_mode):
        """Change command mode.

        :param requested_command_mode:
        :type requested_command_mode: CommandMode
        """
        if requested_command_mode:
            steps = CommandModeHelper.calculate_route_steps(
                self.command_mode, requested_command_mode
            )
            list(map(lambda x: x(self, self._logger), steps))

    def reconnect(self, timeout=None):
        """Reconnect session, keep current command mode.

        :param timeout: Timeout for operation
        """
        prompts_re = r"|".join(
            CommandModeHelper.defined_modes_by_prompt(self.command_mode).keys()
        )
        self.session.reconnect(prompts_re, self._logger, timeout)
        self._initialize(self.command_mode)
