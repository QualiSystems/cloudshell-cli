class Command(object):
    def __init__(self, command, prompt=None, action_map=None, detect_loops=True):
        """
        :param str command:
        :param prompt:
        :param action_map:
        """
        self.command = command
        self.prompt = prompt
        self.action_map = action_map
        self.detect_loops = detect_loops


class CommandResponse(object):
    pass
