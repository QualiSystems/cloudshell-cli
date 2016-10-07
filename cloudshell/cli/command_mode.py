from collections import OrderedDict

from cloudshell.cli.cli_exception import CliException
from cloudshell.cli.node import Node


class CommandModeException(CliException):
    pass


class CommandMode(Node):
    """
    Class describes our prompt and implement enter and exit command functions
    """
    DEFINED_MODES = OrderedDict()

    @staticmethod
    def modes_pattern():
        """
        Generate pattern for defined modes
        :return:
        :rtype: str
        """
        return r'|'.join(CommandMode.DEFINED_MODES.keys())

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

    def step_up(self, cli_operations):
        """
        Enter command mode
        :param cli_operations:
        :type cli_operations: CliOperations
        """
        cli_operations.send_command(self._enter_command, expected_string=self.prompt,
                                    action_map=self._action_map, error_map=self._error_map)
        cli_operations.command_mode = self
        self.default_actions(cli_operations)

    def step_down(self, cli_operations):
        """
        Exit from command mode
        :param cli_operations:
        :type cli_operations: CliOperations
        :return:
        """
        cli_operations.send_command(self._exit_command, expected_string=self.parent_node.prompt,
                                    action_map=self._action_map, error_map=self._error_map)
        cli_operations.command_mode = self.parent_node

    def default_actions(self, cli_operations):
        """
        Default actions
        :param cli_operations:
        :return:
        """
        if self._default_actions:
            self._default_actions(cli_operations)
