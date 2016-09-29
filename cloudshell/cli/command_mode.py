from cloudshell.cli.node import Node
from cloudshell.cli.session.expect_session import ExpectSession


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

    def add_parent_mode(self, mode):
        """
        Add parent mode
        :param mode:
        :type mode: CommandMode
        :return:
        """
        mode.add_child_node(self)
        self.parent_node = mode

    def step_up(self, session):
        """
        Enter command mode
        :param session:
        :type session: ExpectSession
        :return:
        """
        session.hardware_expect(self._enter_command, expected_string=self.prompt,
                                action_map=self._expected_actions,
                                error_map=self._error_map)
        if self._default_actions:
            self._default_actions(session)

    def step_down(self, session):
        """
        Exit from command mode
        :param session:
        :type session: ExpectSession
        :return:
        """
        session.hardware_expect(self._exit_command, expected_string=self.parent_node.prompt,
                                action_map=self._expected_actions,
                                error_map=self._error_map)
