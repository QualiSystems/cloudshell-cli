class Command(object):
    def __init__(self, command, prompt=None, action_map=None):
        """
        :param str command:
        :param prompt:
        :param action_map:
        """
        self.command = command
        self.prompt = prompt
        self.action_map = action_map

class CommandResponse(object):
    pass