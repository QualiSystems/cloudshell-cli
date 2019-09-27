from collections import OrderedDict


class CommandTemplateExecutor(object):
    """Execute command template using cli service."""

    def __init__(
        self,
        cli_service,
        command_template,
        action_map=None,
        error_map=None,
        **optional_kwargs
    ):
        """Initialize Command template executor.

        :param cli_service:
        :type cli_service: CliService
        :param command_template:
        :type command_template: cloudshell.cli.command_template.command_template.CommandTemplate  # noqa: E501
        :param error_map: expected error map with subclass of CommandExecutionException
            or str
        :type error_map: dict[str, cloudshell.cli.session.session_exceptions.CommandExecutionException|str]  # noqa: E501
        """
        self._cli_service = cli_service
        self._command_template = command_template
        self._action_map = action_map or OrderedDict()
        self._error_map = error_map or OrderedDict()
        self._optional_kwargs = optional_kwargs

    @property
    def action_map(self):
        """Return updated action."""
        action_map = self._action_map.copy()
        action_map.update(self._command_template.action_map)
        return action_map

    @property
    def error_map(self):
        error_map = self._error_map.copy()
        error_map.update(self._command_template.error_map)
        return error_map

    @property
    def optional_kwargs(self):
        return self._optional_kwargs

    def execute_command(self, **command_kwargs):
        """Execute command.

        :param command_kwargs:
        :return: Command output
        :rtype: str
        """
        command = self._command_template.prepare_command(**command_kwargs)
        return self._cli_service.send_command(
            command,
            action_map=self.action_map,
            error_map=self.error_map,
            **self.optional_kwargs
        )

    def update_action_map(self, action_map):
        self._action_map.update(action_map)

    def update_error_map(self, error_map):
        self._error_map.update(error_map)

    def update_optional_kwargs(self, **optional_kwargs):
        self.optional_kwargs.update(optional_kwargs)
