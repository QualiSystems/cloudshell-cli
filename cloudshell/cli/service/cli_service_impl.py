from __future__ import annotations

import re
from typing import TYPE_CHECKING

from cloudshell.cli.service.cli_service import CliService
from cloudshell.cli.service.command_mode_helper import CommandModeHelper

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.service.command_mode import CommandMode
    from cloudshell.cli.types import (
        T_ACTION_MAP,
        T_COMMAND_MODE_CONTEXT_MANAGER,
        T_ERROR_MAP,
        T_SESSION,
        T_TIMEOUT,
    )


class EnterCommandModeContextManager:
    def __init__(
        self, cli_service: CliServiceImpl, command_mode: CommandMode, logger: Logger
    ):
        """Context manager used to enter specific command mode.

        These command modes using CommandMode relations
           in CommandMode.RELATIONS_DICT
        """
        self._cli_service = cli_service
        self._command_mode = command_mode
        self._logger = logger
        self._previous_mode = cli_service.command_mode

    def __enter__(self) -> CliServiceImpl:
        self._cli_service._change_mode(self._command_mode)
        return self._cli_service

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:  # if we catch an error throw it upper
            return False

        self._cli_service._change_mode(self._previous_mode)


class EnterDetachCommandModeContextManager(EnterCommandModeContextManager):
    def __init__(
        self, cli_service: CliServiceImpl, command_mode: CommandMode, logger: Logger
    ):
        """Context manager used to enter specific command mode.

        These command modes works without using CommandMode relations
        in CommandMode.RELATIONS_DICT
        """
        super().__init__(cli_service, command_mode, logger)

        if command_mode.parent_node is None:
            command_mode.parent_node = self._previous_mode

    def __enter__(self) -> CliServiceImpl:
        self._command_mode.step_up(self._cli_service, self._logger)
        return self._cli_service

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:  # if we catch an error throw it upper
            return False

        self._command_mode.step_down(self._cli_service, self._logger)


CommandModeContextManager = EnterDetachCommandModeContextManager  # Deprecated


class CliServiceImpl(CliService):
    """Session wrapper, used to keep session mode and enter any child mode."""

    def __init__(
        self, session: T_SESSION, requested_command_mode: CommandMode, logger: Logger
    ):
        super().__init__(session, logger)
        self._initialize(requested_command_mode)

    def _initialize(self, requested_command_mode: CommandMode) -> None:
        self.command_mode = CommandModeHelper.determine_current_mode(
            self.session, requested_command_mode, self._logger
        )
        self.command_mode.enter_actions(self)
        self.command_mode.prompt_actions(self, self._logger)
        self._change_mode(requested_command_mode)

    def enter_mode(self, command_mode: CommandMode) -> T_COMMAND_MODE_CONTEXT_MANAGER:
        """Enter specified command mode."""
        if command_mode.is_attached_command_mode():
            context = EnterCommandModeContextManager
        else:
            context = EnterDetachCommandModeContextManager

        return context(self, command_mode, self._logger)

    def send_command(
        self,
        command: str | None,
        expected_string: str | None = None,
        action_map: T_ACTION_MAP | None = None,
        error_map: T_ERROR_MAP | None = None,
        logger: Logger | None = None,
        remove_prompt: bool = False,
        *args,
        **kwargs,
    ) -> str:
        if not expected_string:
            expected_string = self.command_mode.prompt

        if not logger:
            logger = self._logger
        self.session.logger = logger
        output = self.session.hardware_expect(
            command,
            expected_string=expected_string,
            action_map=action_map,
            error_map=error_map,
            logger=logger,
            *args,
            **kwargs,
        )
        if remove_prompt:
            output = re.sub(rf"^.*{expected_string}.*$", "", output, flags=re.MULTILINE)
        return output

    def _change_mode(self, requested_command_mode: CommandMode) -> None:
        if requested_command_mode:
            steps = CommandModeHelper.calculate_route_steps(
                self.command_mode, requested_command_mode
            )
            for s in steps:
                s(self, self._logger)

    def reconnect(self, timeout: T_TIMEOUT | None = None) -> None:
        """Reconnect session, keep current command mode."""
        prompts_re = r"|".join(
            CommandModeHelper.defined_modes_by_prompt(self.command_mode).keys()
        )
        self.session.reconnect(prompts_re, self._logger, timeout)
        self._initialize(self.command_mode)
