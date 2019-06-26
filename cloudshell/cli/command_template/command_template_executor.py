from collections import OrderedDict

from cloudshell.cli.service.action_map import ActionMap


class CommandTemplateExecutor(object):
    """Execute command template using cli service"""

    def __init__(self, cli_service, command_template, action_map=None, error_map=None, **optional_kwargs):
        """

        :param cloudshell.cli.service.cli_service.CliService cli_service:
        :param cloudshell.cli.command_template.command_template.CommandTemplate command_template:
        :param cloudshell.cli.service.action_map.ActionMap action_map:
        :param error_map: expected error map with subclass of CommandExecutionException or str
        :type error_map: dict[str, cloudshell.cli.session.session_exceptions.CommandExecutionException|str]
        :return:
        """
        self._cli_service = cli_service
        self._command_template = command_template

        self._action_map = action_map or ActionMap()
        self._action_map.extend(command_template.action_map)

        self._error_map = error_map or OrderedDict()
        self._error_map.update(command_template.error_map)

        self._optional_kwargs = optional_kwargs

    def execute_command(self, **command_kwargs):
        """

        :param dict command_kwargs:
        :return: Command output
        :rtype: str
        """
        command = self._command_template.prepare_command(**command_kwargs)
        return self._cli_service.send_command(command,
                                              action_map=self._action_map,
                                              error_map=self._error_map,
                                              **self._optional_kwargs)
