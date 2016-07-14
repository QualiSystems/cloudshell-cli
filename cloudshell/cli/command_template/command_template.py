__author__ = 'g8y3e'


class CommandTemplate:
    def __init__(self, command, re_string_list=[], error_message_list=[]):
        self._command = command

        self._re_string_list = []
        if isinstance(re_string_list, list):
            self._re_string_list += re_string_list
        else:
            self._re_string_list = [re_string_list]

        self._error_message_list = []
        if isinstance(error_message_list, list):
            self._error_message_list += error_message_list
        else:
            self._error_message_list = [error_message_list]

    def get_error_by_index(self, index):
        if (len(self._error_message_list) - 1) < index:
            raise Exception('Command Template: '
                            'Failed to get index from error_message_list, error index higher than error_message_list size!')

        return self._error_message_list[index]

    def get_re_string_list(self):
        return self._re_string_list

    def get_command(self, *args):
        return self._command.format(*args)
