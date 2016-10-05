from collections import OrderedDict

from cloudshell.cli.node import Node
from cloudshell.cli.session.session import Session


class CommandModeException(Exception):
    pass


class CommandMode(Node):
    """
    Class describes our prompt and implement enter and exit command functions
    """
    DEFINED_MODES = OrderedDict()

    def __init__(self, prompt, enter_command, exit_command, default_actions=None, action_map={}, error_map={},
                 parent_mode=None):
        """
            :param prompt:
            :param enter_command:
            :param exit_command:
            :param default_action:
            :param expected_map:
            :param error_map:
            :param parent_mode:
            :return:
            """
        super(CommandMode, self).__init__()
        self.prompt = prompt
        self._enter_command = enter_command
        self._exit_command = exit_command
        self._default_actions = default_actions
        self._action_map = action_map
        self._error_map = error_map
        if parent_mode:
            self.add_parent_mode(parent_mode)
        CommandMode.DEFINED_MODES[self.prompt] = self

    def add_parent_mode(self, mode):
        """
        Add parent mode
        :param mode:
        :type mode: CommandMode
        :return:
        """
        mode.add_child_node(self)

    def step_up(self, session, logger):
        """
        Enter command mode
        :param session:
        :type session: Session
        :return:
        """
        session.hardware_expect(self._enter_command, logger=logger, expected_string=self.prompt,
                                action_map=self._action_map, error_map=self._error_map)
        if self._default_actions:
            self._default_actions(session, logger)

    def step_down(self, session, logger):
        """
        Exit from command mode
        :param session:
        :type session: Session
        :return:
        """
        session.hardware_expect(self._exit_command, logger=logger, expected_string=self.parent_node.prompt,
                                action_map=self._action_map, error_map=self._error_map)
