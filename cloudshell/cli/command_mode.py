from collections import OrderedDict
from cloudshell.cli.cli_exception import CliException

from cloudshell.cli.node import Node
from cloudshell.cli.cli_operations import CliOperations


class CommandModeException(CliException):
    pass


class CommandMode(Node):
    """
    Class describes our prompt and implement enter and exit command functions
    """
    DEFINED_MODES = OrderedDict()

    def __init__(self, prompt, enter_command, exit_command, default_actions=None, action_map={}, error_map={},
                 parent_mode=None):
        """
            :param prompt: Prompt of this mode
            :type prompt: str
            :param enter_command: Command used to enter this mode
            :type enter_command: str
            :param exit_command: Command used to exit from this mode
            :type exit_command: str
            :param default_actions: Actions which needs to be done when entering this mode
            :param action_map: Any expected actions
            :param error_map: Defined error map
            :param parent_mode: Connect parent mode
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
        :type session: CliOperations
        :return:
        """
        session.send_command(self._enter_command, logger=logger, expected_string=self.prompt,
                             action_map=self._action_map, error_map=self._error_map)
        if self._default_actions:
            self._default_actions(session, logger)

    def step_down(self, session, logger):
        """
        Exit from command mode
        :param session:
        :type session: CliOperations
        :return:
        """
        session.send_command(self._exit_command, logger=logger, expected_string=self.parent_node.prompt,
                             action_map=self._action_map, error_map=self._error_map)
