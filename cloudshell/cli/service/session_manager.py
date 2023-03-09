from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.types import T_SESSION


class SessionManager(ABC):
    @abstractmethod
    def new_session(
        self, new_sessions: list[T_SESSION] | T_SESSION, prompt: str, logger: Logger
    ) -> T_SESSION:
        """Create new session with specific session type defined in sessions_params."""
        pass

    @abstractmethod
    def existing_sessions_count(self) -> int:
        pass

    @abstractmethod
    def remove_session(self, session: T_SESSION, logger: Logger) -> None:
        """Remove session."""
        pass

    @abstractmethod
    def is_compatible(
        self,
        session: T_SESSION,
        new_sessions: list[T_SESSION] | T_SESSION,
        logger: Logger,
    ) -> bool:
        """Compare session type and connection attributes."""
        pass
