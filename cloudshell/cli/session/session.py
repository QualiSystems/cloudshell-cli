from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.types import T_ACTION_MAP, T_ERROR_MAP, T_TIMEOUT


class Session(ABC):
    @abstractmethod
    def connect(self, prompt: str, logger: Logger) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def _send(self, command: str, logger: Logger) -> None:
        pass

    @abstractmethod
    def send_line(self, command: str, logger: Logger) -> None:
        pass

    @abstractmethod
    def _receive(self, timeout: T_TIMEOUT, logger: Logger) -> str:
        pass

    @abstractmethod
    def hardware_expect(
        self,
        command: str | None,
        expected_string: str,
        logger: Logger,
        action_map: T_ACTION_MAP | None = None,
        error_map: T_ERROR_MAP | None = None,
        timeout: T_TIMEOUT | None = None,
        retries: int | None = None,
        check_action_loop_detector: bool = True,
        empty_loop_timeout: T_TIMEOUT | None = None,
        **optional_args,
    ) -> str:
        pass

    @abstractmethod
    def probe_for_prompt(self, expected_string: str, logger: Logger) -> str:
        pass

    @abstractmethod
    def match_prompt(self, prompt: str, match_string: str, logger: Logger) -> bool:
        pass

    @abstractmethod
    def reconnect(
        self, prompt: str, logger: Logger, timeout: T_TIMEOUT | None = None
    ) -> None:
        pass

    @abstractmethod
    def active(self) -> bool:
        pass

    @abstractmethod
    def set_active(self, state: bool) -> None:
        pass
