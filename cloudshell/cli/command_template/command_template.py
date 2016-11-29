from collections import OrderedDict

import re
from cloudshell.cli.cli_service import CliService


class CommandTemplateExecutor(object):
    """
    Execute command template using cli service
    """

    def __init__(self, cli_service, command_template):
        """
        :param cli_service:
        :type cli_service: CliService
        :param command_template:
        :type command_template: CommandTemplate
        :return:
        """
        self._cli_service = cli_service
        self._command_template = command_template
        self._action_map = OrderedDict()
        self._error_map = OrderedDict()

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
        command = self._command_template.get_raw_command(**command_kwargs)
        self._cli_service.send_command(command, action_map=self.action_map, error_map=self.error_map)

    def update_action_map(self, action_map):
        self._action_map.update(action_map)

    def update_error_map(self, error_map):
        self._error_map.update(error_map)


class CommandTemplate:
    """
    Command template class
    """

    def __init__(self, command, action_map=OrderedDict(), error_map=OrderedDict()):
        """
        :param command:
        :type command: basestring
        :param action_map:
        :type action_map: OrderedDict
        :param error_map:
        :type error_map: OrderedDict
        """
        self._command = command
        self._action_map = action_map
        self._error_map = error_map

    @property
    def action_map(self):
        """
        :rtype: dict
        """
        return self._action_map

    @property
    def error_map(self):
        """
        :rtype: dict
        """
        return self._error_map

    def get_raw_command(self, **command_kwargs):
        """
        Generate command string from command template
        :param command_kwargs:
        :type command_kwargs: dict
        :return:
        :rtype: basestring
        """
        return self._prepare_command(**command_kwargs)

    def get_command(self, action_map=OrderedDict(), error_map=OrderedDict(), **command_kwargs):
        """
        Generate dict for cli_service signature with action map and error map
        :param action_map:
        :type action_map: dict
        :param error_map:
        :type error_map: dict
        :param command_kwargs:
        :type command_kwargs: dict
        :return:
        :rtype: dict
        """
        action_map.update(self.action_map)
        error_map.update(self.error_map)
        return {
            'command': self._prepare_command(**command_kwargs),
            'action_map': action_map,
            'error_map': error_map
        }

    def _prepare_command(self, **kwargs):
        cmd = self._command
        keys = re.findall(r"{(\w+)}", self._command)
        for key in keys:
            if key not in kwargs or kwargs[key] is None:
                cmd = re.sub(r"(^.* )(\[.*{{{key}}}\])(.*)".format(key=key), r"\1\3", cmd)

        if not cmd:
            raise Exception(self.__class__.__name__, 'Unable to prepare command')

        cmd = re.sub(r"\s+", " ", cmd).strip(' \t\n\r')
        result = re.sub(r"\[|\]", "", cmd).format(**kwargs)
        return result
