from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate


class CommandTemplateExecutor(object):
    """
    Execute command template using cli service
    """

    def __init__(self, cli_service, command_template, action_map=None, error_map=None, **optional_kwargs):
        """
        :param cli_service:
        :type cli_service: CliService
        :param command_template:
        :type command_template: CommandTemplate
        :return:
        """
        self._cli_service = cli_service
        self._command_template = command_template
        self._action_map = action_map or OrderedDict()
        self._error_map = error_map or OrderedDict()
        self._optional_kwargs = optional_kwargs

    @property
    def action_map(self):
        """
        Return updated action
        """
        return OrderedDict(self._action_map.items() + self._command_template.action_map.items())

    @property
    def error_map(self):
        return OrderedDict(self._command_template.error_map.items() + self._error_map.items())

    @property
    def optional_kwargs(self):
        return self._optional_kwargs

    def execute_command(self, **command_kwargs):
        command = self._command_template.prepare_command(**command_kwargs)
        return self._cli_service.send_command(command, action_map=self.action_map, error_map=self.error_map,
                                              **self.optional_kwargs)

    def update_action_map(self, action_map):
        self._action_map.update(action_map)

    def update_error_map(self, error_map):
        self._error_map.update(error_map)

    def update_optional_kwargs(self, **optional_kwargs):
        self.optional_kwargs.update(optional_kwargs)
