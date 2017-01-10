from cloudshell.cli.cli_exception import CliException
from cloudshell.cli.node import Node


class CommandModeException(CliException):
    pass


class CommandMode(Node):
    """
    Class describes our prompt and implement enter and exit command functions
    """

    RELATIONS_DICT = {}

    def __init__(self, prompt, enter_command=None, exit_command=None, enter_action_map=None, exit_action_map=None,
                 enter_error_map=None, exit_error_map=None, parent_mode=None, enter_actions=None):
        """
            :param prompt: Prompt of this mode
            :type prompt: str
            :param enter_command: Command used to enter this mode
            :type enter_command: str
            :param exit_command: Command used to exit from this mode
            :type exit_command: str
            :param enter_actions: Actions which needs to be done when entering this mode
            :param enter_action_map: Enter expected actions
            :type enter_action_map: dict
            :param enter_error_map: Enter error map
            :type enter_error_map: dict
            :param exit_action_map:
            :type exit_action_map: dict
            :param exit_error_map:
            :type exit_error_map: dict
            :param
            :param parent_mode: Connect parent mode
            """
        if not exit_error_map:
            exit_error_map = {}
        if not enter_error_map:
            enter_error_map = {}
        if not exit_action_map:
            exit_action_map = {}
        if not enter_action_map:
            enter_action_map = {}

        super(CommandMode, self).__init__()
        self.prompt = prompt
        self._enter_command = enter_command
        self._exit_command = exit_command
        self._enter_action_map = enter_action_map
        self._exit_action_map = exit_action_map
        self._enter_error_map = enter_error_map
        self._exit_error_map = exit_error_map
        self._enter_actions = enter_actions

        if parent_mode:
            self.add_parent_mode(parent_mode)

    def add_parent_mode(self, mode):
        """
        Add parent mode
        :param mode:
        :type mode: CommandMode
        :return:
        """
        if mode:
            mode.add_child_node(self)

    def step_up(self, cli_service):
        """
        Enter command mode
        :param cli_service:
        :type cli_service: CliService
        """
        cli_service.send_command(self._enter_command, expected_string=self.prompt,
                                 action_map=self._enter_action_map, error_map=self._enter_error_map)
        cli_service.command_mode = self
        self.enter_actions(cli_service)

    def step_down(self, cli_service):
        """
        Exit from command mode
        :param cli_service:
        :type cli_service: CliService
        :return:
        """
        cli_service.send_command(self._exit_command, expected_string=self.parent_node.prompt,
                                 action_map=self._exit_action_map, error_map=self._exit_error_map)
        cli_service.command_mode = self.parent_node

    def enter_actions(self, cli_service):
        """
        Default actions
        :param cli_service:
        :type cli_service: CliService
        :return:
        """
        if self._enter_actions:
            self._enter_actions(cli_service)
