from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cloudshell.cli.command_template.command_template import CommandTemplate
    from cloudshell.cli.service.cli_service import CliService
    from cloudshell.cli.types import T_ACTION_MAP, T_ERROR_MAP


class CommandTemplateExecutor:
    """Execute command template using cli service."""

    def __init__(
        self,
        cli_service: CliService,
        command_template: CommandTemplate,
        action_map: T_ACTION_MAP | None = None,
        error_map: T_ERROR_MAP | None = None,
        **optional_kwargs,
    ):
        self._cli_service = cli_service
        self._command_template = command_template
        self._action_map = action_map or OrderedDict()
        self._error_map = error_map or OrderedDict()
        self._optional_kwargs = optional_kwargs

    @property
    def action_map(self) -> T_ACTION_MAP:
        """Return updated action."""
        action_map = self._action_map.copy()
        action_map.update(self._command_template.action_map)
        return action_map

    @property
    def error_map(self) -> T_ERROR_MAP:
        error_map = self._error_map.copy()
        error_map.update(self._command_template.error_map)
        return error_map

    @property
    def optional_kwargs(self) -> dict:
        return self._optional_kwargs

    def execute_command(self, **command_kwargs) -> str:
        command = self._command_template.prepare_command(**command_kwargs)
        return self._cli_service.send_command(
            command,
            action_map=self.action_map,
            error_map=self.error_map,
            **self.optional_kwargs,
        )

    def update_action_map(self, action_map: T_ACTION_MAP) -> None:
        self._action_map.update(action_map)

    def update_error_map(self, error_map: T_ERROR_MAP) -> None:
        self._error_map.update(error_map)

    def update_optional_kwargs(self, **optional_kwargs: dict) -> None:
        self.optional_kwargs.update(optional_kwargs)
