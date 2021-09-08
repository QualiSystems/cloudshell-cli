from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from cloudshell.cli.session.prompt.prompt import AbstractPrompt
    from cloudshell.cli.process.actions.action_map import ActionMap
    from cloudshell.cli.process.command.reader import ResponseBuffer


class Command(object):
    def __init__(self, command: str,
                 prompt: Optional["AbstractPrompt"] = None,
                 action_map: Optional["ActionMap"] = None,
                 detect_loops: bool = True,
                 read_timeout: Optional[int] = None,
                 clear_buffer: bool = True):
        """
        :param str command:
        :param prompt:
        :param action_map:
        """
        self.command = command
        self.prompt = prompt
        self.action_map = action_map
        self.detect_loops = detect_loops
        self.read_timeout = read_timeout
        self.clear_buffer = clear_buffer

    def __str__(self):
        return self.command


class CommandResponse(object):
    def __init__(self, response_buffer: "ResponseBuffer"):
        self.response_buffer = response_buffer

    def get_data(self):
        return str(self.response_buffer)

    def __str__(self):
        return self.get_data()
