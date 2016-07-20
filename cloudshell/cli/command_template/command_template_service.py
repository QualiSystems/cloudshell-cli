from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.cli.command_template.command_template_validator import get_validate_list

_TEMPLATE_DICT = {}


def add_templates(commands):
    _TEMPLATE_DICT.update(commands)


def send_commands_list(commands_list, send_command_func=None, expected_map=None, error_map=None, **optional_args):
    if not send_command_func:
        raise Exception('send_commands_list', 'send_command function is None or empty')
    output = ''
    for command in commands_list:
        out = send_command_func(command, expected_map=expected_map, error_map=error_map, **optional_args)
        if out:
            output += out
    return output


def execute_command_map(command_map, send_command_func=None, expected_map=None, error_map=None):
    """Generate commands list based on command_map and run them

    :param command_map: map of commands
    :param send_command_func: reference to send_command

    :return: aggregated commands output
    :rtype: string
    """

    commands_list = get_commands_list(command_map)
    output = send_commands_list(commands_list, send_command_func, expected_map=expected_map, error_map=error_map)
    return output


def get_commands_list(command_map):
    """Generate list of commands based on provided command_map using _TEMPLATE_DICT

    :param command_map:
    :return: list of commands
    """

    prepared_commands = []
    for command, value in command_map.items():
        if isinstance(command, CommandTemplate):
            command_template = command
        else:
            if command in _TEMPLATE_DICT:
                command_template = _TEMPLATE_DICT[command]

            else:
                raise Exception("get_commands_list: ", "Command template \'{0}\' is not registered".format(command))
        prepared_commands.append(get_validate_list(command_template, value))
    return prepared_commands
