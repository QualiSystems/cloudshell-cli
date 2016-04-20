from cloudshell.cli.command_template.command_template_validator import get_validate_list

_TEMPLATE_DICT = {}


def add_templates(commands):
    _TEMPLATE_DICT.update(commands)


def send_commands_list(commands_list, send_command_func=None):
    if not send_command_func:
        raise Exception("Need send command function")
    output = ""
    for command in commands_list:
        out = send_command_func(command)
        if out:
            output += out
    return output


def execute_command_map(command_map, send_command_func=None):
    """
    Configures interface ethernet
    :param kwargs: dictionary of parameters
    :return: success message
    :rtype: string
    """

    commands_list = get_commands_list(command_map)
    output = send_commands_list(commands_list, send_command_func)
    return output


def get_commands_list(command_map):
    prepared_commands = []
    for command, value in command_map.items():
        if command in _TEMPLATE_DICT:
            command_template = _TEMPLATE_DICT[command]
            prepared_commands.append(get_validate_list(command_template, value))
    return prepared_commands
