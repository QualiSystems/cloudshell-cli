from __future__ import annotations

import re
from typing import TYPE_CHECKING

from cloudshell.cli.service.cli_exception import CliException
from cloudshell.cli.service.node import Node

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from logging import Logger

    from cloudshell.cli.service.cli_service import CliService
    from cloudshell.cli.types import T_ACTION_MAP, T_COMMAND_MODE_RELATIONS, T_ERROR_MAP


class CommandModeException(CliException):
    pass


class CommandMode(Node):
    """Class describes our prompt and implement enter and exit command functions."""

    RELATIONS_DICT = {}

    def __init__(
        self,
        prompt: str,
        enter_command: str | None = None,
        exit_command: str | None = None,
        enter_action_map: T_ACTION_MAP | None = None,
        exit_action_map: T_ACTION_MAP | None = None,
        enter_error_map: T_ERROR_MAP | None = None,
        exit_error_map: T_ERROR_MAP | None = None,
        parent_mode: CommandMode | None = None,
        enter_actions: Callable[[CliService], None] | None = None,
        use_exact_prompt: bool = False,
    ):
        """Initialize Command Mode.

        :param prompt: Prompt of this mode
        :param enter_command: Command used to enter this mode
        :param exit_command: Command used to exit from this mode
        :param enter_actions: Actions which needs to be done when entering this mode
        """
        if not exit_error_map:
            exit_error_map = {}
        if not enter_error_map:
            enter_error_map = {}
        if not exit_action_map:
            exit_action_map = {}
        if not enter_action_map:
            enter_action_map = {}

        super().__init__()
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
    def prompt(self) -> str:
        if self._use_exact_prompt and self._exact_prompt:
            return self._exact_prompt
        else:
            return self._prompt

    @prompt.setter
    def prompt(self, value: str) -> None:
        self._prompt = value

    def add_parent_mode(self, mode: CommandMode | None) -> None:
        if mode:
            mode.add_child_node(self)

    def step_up(self, cli_service: CliService, logger: Logger) -> None:
        if not isinstance(self._enter_command, (list, tuple)):
            enter_command_list = [self._enter_command]
        else:
            enter_command_list = self._enter_command
        for enter_command in enter_command_list:
            cli_service.send_command(
                enter_command,
                expected_string=self.prompt,
                action_map=self._enter_action_map,
                error_map=self._enter_error_map,
            )
        cli_service.command_mode = self
        self.enter_actions(cli_service)
        self.prompt_actions(cli_service, logger)

    def step_down(self, cli_service: CliService, logger: Logger) -> None:
        if not isinstance(self._exit_command, (list, tuple)):
            exit_command_list = [self._exit_command]
        else:
            exit_command_list = self._exit_command
        for exit_command in exit_command_list:
            cli_service.send_command(
                exit_command,
                expected_string=self.parent_node.prompt,
                action_map=self._exit_action_map,
                error_map=self._exit_error_map,
            )
        cli_service.command_mode = self.parent_node

    def enter_actions(self, cli_service: CliService) -> None:
        if self._enter_actions:
            self._enter_actions(cli_service)

    def prompt_actions(self, cli_service: CliService, logger: Logger) -> None:
        if self._use_exact_prompt:
            self._exact_prompt = self._initialize_exact_prompt(cli_service, logger)
            logger.debug("Exact prompt: " + self._exact_prompt)

    def _initialize_exact_prompt(self, cli_service: CliService, logger: Logger) -> str:
        if self._exact_prompt:
            return self._exact_prompt

        output = cli_service.session.probe_for_prompt(self._prompt, logger)
        match = re.search(self._prompt, output, re.DOTALL)
        if match.groups():
            exact_prompt = match.group(1)
        else:
            exact_prompt = output.strip().splitlines()[-1].strip()
        exact_prompt = re.escape(exact_prompt)

        if not re.search(exact_prompt, output, re.DOTALL):
            raise Exception(
                self.__class__.__name__, "Exact prompt is not matching the output"
            )

        return exact_prompt

    @classmethod
    def get_all_attached_command_modes(
        cls, relations_dict: T_COMMAND_MODE_RELATIONS | None = None
    ) -> Generator[type[CommandMode], None, None]:
        if relations_dict is None:
            relations_dict = cls.RELATIONS_DICT

        for key, val in relations_dict.items():
            yield key

            if isinstance(val, dict):
                for key in cls.get_all_attached_command_modes(val):
                    yield key

    def is_attached_command_mode(self) -> bool:
        return isinstance(self, tuple(self.get_all_attached_command_modes()))
