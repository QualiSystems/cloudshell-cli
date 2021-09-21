from cloudshell.cli.session.advanced_session.actions.action_map import ActionMap
from cloudshell.cli.session.advanced_session.actions.error_map import ErrorMap


class CommandTemplateExecutor(object):
    """Execute command template using cli service."""

    def __init__(
        self,
        command_processor,
        command_template,
        action_map=None,
        error_map=None):
        """Initialize Command template executor.

        :param cloudshell.cli.service.cli_service.CliService command_processor:
        :param cloudshell.cli.command_template.command_template.CommandTemplate command_template:
        :param cloudshell.cli.service.action_map.ActionMap action_map:
        :param cloudshell.cli.service.error_map.ErrorMap error_map:
        :return:
        """
        self._command_processor = command_processor
        self._command_template = command_template

        self._action_map = action_map or ActionMap()
        self._action_map.extend(command_template.action_map)

        self._error_map = error_map or ErrorMap()
        self._error_map.extend(command_template.error_map)

        self._optional_kwargs = optional_kwargs

    def execute_command(self, **command_kwargs):
        """Execute command.

        :param dict command_kwargs:
        :return: Command output
        :rtype: str
        """
        command = self._command_template.prepare_command(**command_kwargs)
        return self._cli_service.send_command(command,
                                              action_map=self._action_map,
                                              error_map=self._error_map,
                                              **self._optional_kwargs)
