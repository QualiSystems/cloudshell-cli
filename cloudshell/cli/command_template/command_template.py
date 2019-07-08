import re

from cloudshell.cli.service.action_map import ActionMap
from cloudshell.cli.service.error_map import ErrorMap


class CommandTemplate:
    def __init__(self, command, action_map=None, error_map=None):
        """

        :param str command:
        :param cloudshell.cli.service.action_map.ActionMap action_map:
        :param cloudshell.cli.service.error_map.ErrorMap error_map:
        """
        self._command = command
        self._action_map = action_map or ActionMap()
        self._error_map = error_map or ErrorMap()

    @property
    def action_map(self):
        """

        :rtype: cloudshell.cli.service.action_map.ActionMap
        """
        return self._action_map

    @property
    def error_map(self):
        """

        :rtype: cloudshell.cli.service.error_map.ErrorMap
        """
        return self._error_map

    # ToDo: Needs to be reviewed
    def get_command(self, **kwargs):
        """

        :param dict kwargs:
        :rtype: dict
        """
        action_map = kwargs.get('action_map') or ActionMap()
        action_map.extend(self.action_map)

        error_map = kwargs.get("error_map") or ErrorMap()
        error_map.extend(self.error_map)

        return {
            'command': self.prepare_command(**kwargs),
            'action_map': action_map,
            'error_map': error_map
        }

    def prepare_command(self, **kwargs):
        """

        :param dict kwargs:
        :rtype: str
        """
        cmd = self._command
        keys = re.findall(r"{(\w+)}", self._command)
        for key in keys:
            if key not in kwargs or kwargs[key] is None:
                cmd = re.sub(r"\[[^[]*?{{{key}}}.*?\]".format(key=key), r"", cmd)

        if not cmd:
            raise Exception("Unable to prepare command")

        cmd = re.sub(r"\s+", " ", cmd).strip(' \t\n\r')
        result = re.sub(r"\[|\]", "", cmd).format(**kwargs)
        return result
