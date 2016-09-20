from cloudshell.cli.node import Node


class CommandMode(Node):
    """
    Class describes our prompt and implement enter and exit command functions
    """
    DEFINED_PROMPTS = []

    def __init__(self, prompt, enter_command, exit_command, default_action=None, expected_map=None, error_map=None):
        """
            :param prompt:
            :param enter_command:
            :param exit_command:
            :param default_action:
            :param expected_map:
            :param error_map:
            :return:
            """
        super(CommandMode, self).__init__()
        self.prompt = prompt
        self._enter_command = enter_command
        self._exit_command = exit_command
        self._default_actions = default_action
        self._expected_actions = expected_map
        self._error_map = error_map

    def connect_mode(self, command_mode):
        """
        Connect child mode
        :param command_mode:
        :return:
        """
        self.add_child_node(command_mode)
        CommandMode.DEFINED_PROMPTS.append(command_mode)

    def step_up(self, session):
        session.hardware_expect(self._enter_command, expected_string=self.prompt,
                                expected_actions=self._expected_actions,
                                error_map=self._error_map)

    def step_down(self, session):
        session.hardware_expect(self._exit_command, expected_string=self.parent_node.prompt,
                                expected_actions=self._expected_actions,
                                error_map=self._error_map)
