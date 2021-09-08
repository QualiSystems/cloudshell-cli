import re
from functools import lru_cache

_color_pattern_ = re.compile(
    r"\[[0-9]+;{0,1}[0-9]+m|\[[0-9]+m|\b|" + chr(27)
)  # 27 - ESC character


def normalize_buffer(input_buffer):
    """Method for clear color fro input_buffer and special characters.

    :param str input_buffer: input buffer string from device
    :return: str
    """

    result_buffer = ""

    match_iter = _color_pattern_.finditer(input_buffer)

    current_index = 0
    for match_color in match_iter:
        match_range = match_color.span()
        result_buffer += input_buffer[current_index: match_range[0]]
        current_index = match_range[1]

    result_buffer += input_buffer[current_index:]

    result_buffer = result_buffer.replace("\r\n", "\n")

    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]", "", result_buffer)


@lru_cache()
def command_pattern(command):
    """Generate command_pattern.

    :param command:
    :return:
    """
    return re.compile("\\s*" + re.sub(r"\\\s+", r"\\s+", re.escape(command)) + "\\s*", re.MULTILINE)


def remove_command(buffer, command):
    """
    :param cloudshell.cli.session.advanced_session.model.session_reader.SessionBuffer buffer:
    :param str command:
    :return:
    """

    if command and not buffer.command_removed:
        if not buffer.command_removed and command_pattern(command).search(buffer.get_last()):
            buffer.replace_last(command_pattern(command).sub("", buffer.get_last(), count=1))
            buffer.command_removed = True
