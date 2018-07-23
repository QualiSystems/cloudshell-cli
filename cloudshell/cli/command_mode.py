from cloudshell.cli.cli_exception import CliException
from cloudshell.cli.cli_service import CliService
from cloudshell.cli.node import Node


class CommandModeException(CliException):
    pass


class CommandMode(Node):
    """
    Class describes our prompt and implement enter and exit command functions
    """

    RELATIONS_DICT = {}

    def __init__(self, prompt, enter_command=None, exit_command=None, enter_action_map=None, exit_action_map=None,
                 enter_error_map=None, exit_error_map=None, parent_mode=None, enter_actions=None,
                 use_exact_prompt=False):
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
        self._prompt = prompt
        self._exact_prompt = None
        self._enter_command = enter_command
        self._exit_command = exit_command
        self._enter_action_map = enter_action_map
        self._exit_action_map = exit_action_map
        self._enter_error_map = enter_error_map
        self._exit_error_map = exit_error_map
        self._enter_actions = enter_actions
        self._use_exact_prompt = use_exact_prompt

        if parent_mode:
            self.add_parent_mode(parent_mode)

    @property
    def prompt(self):
        if self._use_exact_prompt and self._exact_prompt:
            return self._exact_prompt
        else:
            return self._prompt

    @prompt.setter
    def prompt(self, value):
        self._prompt = value

    def add_parent_mode(self, mode):
        """
        Add parent mode
        :param mode:
        :type mode: CommandMode
        :return:
        """
        if mode:
            mode.add_child_node(self)

    def step_up(self, cli_service, logger):
        """
        Enter command mode
        :param cli_service:
        :type cli_service: CliService
        :type logger: logging.Logger
        """

        if not isinstance(self._enter_command, (list, tuple)):
            enter_command_list = [self._enter_command]
        else:
            enter_command_list = self._enter_command
        for enter_command in enter_command_list:
            cli_service.send_command(enter_command, expected_string=self.prompt,
                                     action_map=self._enter_action_map, error_map=self._enter_error_map)
        cli_service.command_mode = self
        self.enter_actions(cli_service)
        self.prompt_actions(cli_service, logger)

    def step_down(self, cli_service, logger):
        """
        Exit from command mode
        :param cli_service:
        :type cli_service: CliService
        :type logger: logging.Logger
        """
        if not isinstance(self._exit_command, (list, tuple)):
            exit_command_list = [self._exit_command]
        else:
            exit_command_list = self._exit_command
        for exit_command in exit_command_list:
            cli_service.send_command(exit_command, expected_string=self.parent_node.prompt,
                                     action_map=self._exit_action_map, error_map=self._exit_error_map)
        cli_service.command_mode = self.parent_node

    def enter_actions(self, cli_service):
        """
        Default actions
        :type cli_service: cloudshell.cli.cli_service.CliService
        """

        if self._enter_actions:
            self._enter_actions(cli_service)

    def prompt_actions(self, cli_service, logger):
        """
        Prompt actions
        :type cli_service: cloudshell.cli.cli_service.CliService
        :type logger: logging.Logger
        """
        if self._use_exact_prompt:
            self._exact_prompt = cli_service.session.exact_prompt(self._prompt, logger)
            logger.debug('Exact prompt: ' + self._exact_prompt)
