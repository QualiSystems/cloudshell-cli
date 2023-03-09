from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

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


class CliService(ABC):
    def __init__(self, session: T_SESSION, logger: Logger):
        self.session = session
        self._logger = logger

    @abstractmethod
    def send_command(
        self,
        command: str | None,
        expected_string: str | None = None,
        action_map: T_ACTION_MAP | None = None,
        error_map: T_ERROR_MAP | None = None,
        logger: Logger | None = None,
        *args,
        **kwargs,
    ) -> str:
        pass

    @abstractmethod
    def enter_mode(self, command_mode: CommandMode) -> T_COMMAND_MODE_CONTEXT_MANAGER:
        pass

    @abstractmethod
    def reconnect(self, timeout: T_TIMEOUT | None = None) -> None:
        pass
