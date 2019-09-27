import re


def normalize_buffer(input_buffer):
    """Method for clear color fro input_buffer and special characters.

    :param str input_buffer: input buffer string from device
    :return: str
    """
    color_pattern = re.compile(
        r"\[[0-9]+;{0,1}[0-9]+m|\[[0-9]+m|\b|" + chr(27)
    )  # 27 - ESC character

    result_buffer = ""

    match_iter = color_pattern.finditer(input_buffer)

    current_index = 0
    for match_color in match_iter:
        match_range = match_color.span()
        result_buffer += input_buffer[current_index : match_range[0]]
        current_index = match_range[1]

    result_buffer += input_buffer[current_index:]

    result_buffer = result_buffer.replace("\r\n", "\n")

    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]", "", result_buffer)
