from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate


class CommandTemplateExecutor(object):
    """
    Execute command template using cli service
    """

    def __init__(self, cli_service, command_template, action_map=OrderedDict(), error_map=OrderedDict()):
        """
        :param cli_service:
        :type cli_service: CliService
        :param command_template:
        :type command_template: CommandTemplate
        :return:
        """
        self._cli_service = cli_service
        self._command_template = command_template
        self._action_map = action_map
        self._error_map = error_map

    @property
    def action_map(self):
        """
        Return updated action
        """
        return self._action_map.copy().update(self._command_template.action_map)

    @property
    def error_map(self):
        return self._command_template.error_map.copy().update(self._error_map)

    def execute_command(self, **command_kwargs):
        command = self._command_template.prepare_command(**command_kwargs)
        self._cli_service.send_command(command, action_map=self.action_map, error_map=self.error_map)

    def update_action_map(self, action_map):
        self._action_map.update(action_map)

    def update_error_map(self, error_map):
        self._error_map.update(error_map)
