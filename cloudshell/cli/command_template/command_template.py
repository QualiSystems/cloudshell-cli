from collections import OrderedDict
import re


class CommandTemplate:
    def __init__(self, command, action_map=None, error_map=None):
        self._command = command
        self._action_map = action_map or OrderedDict()
        self._error_map = error_map or OrderedDict()

    @property
    def action_map(self):
        """
        Property for action map
        :return:
        :rtype: OrderedDict()
        """
        return self._action_map

    @property
    def error_map(self):
        """
        Property for error map
        :return:
        :rtype: OrderedDict
        """
        return self._error_map

    # ToDo: Needs to be reviewed
    def get_command(self, **kwargs):
        action_map = (OrderedDict(kwargs.get('action_map', None) or OrderedDict()))
        action_map.update(self._action_map)
        error_map = OrderedDict(self._error_map)
        error_map.update(kwargs.get('error_map', None) or OrderedDict())
        return {
            'command': self.prepare_command(**kwargs),
            'action_map': action_map,
            'error_map': error_map
        }

    def prepare_command(self, **kwargs):
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
