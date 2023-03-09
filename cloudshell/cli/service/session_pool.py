from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.types import T_SESSION


class SessionPool(ABC):
    @abstractmethod
    def get_session(
        self, new_sessions: list[T_SESSION], prompt: str, logger: Logger
    ) -> T_SESSION:
        """Get session from pool."""
        pass

    @abstractmethod
    def return_session(self, session: T_SESSION, logger: Logger) -> None:
        """Return session to pool."""
        pass

    @abstractmethod
    def remove_session(self, session: T_SESSION, logger: Logger) -> None:
        """Remove session from pool."""
        pass
