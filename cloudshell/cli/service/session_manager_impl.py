from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.cli.service.cli_exception import CliException
from cloudshell.cli.service.session_manager import SessionManager

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.types import T_SESSION


class SessionManagerException(CliException):
    pass


class SessionManagerImpl(SessionManager):
    def __init__(self):
        self._existing_sessions: list[T_SESSION] = []

    def new_session(
        self, new_sessions: list[T_SESSION] | T_SESSION, prompt: str, logger: Logger
    ) -> T_SESSION:
        """Create new session."""
        if not isinstance(new_sessions, list):
            new_sessions = [new_sessions]

        for session in new_sessions:
            try:
                session.connect(prompt, logger)
                logger.debug(f"Created new {session.session_type} session")
                self._existing_sessions.append(session)
                return session
            except Exception as e:
                logger.debug(e)
        raise SessionManagerException(
            self.__class__.__name__,
            "Failed to create new session for type {}, see logs for details".format(
                ", ".join([session.session_type for session in new_sessions])
            ),
        )

    def existing_sessions_count(self) -> int:
        return len(self._existing_sessions)

    def remove_session(self, session: T_SESSION, logger: Logger) -> None:
        if session in self._existing_sessions:
            self._existing_sessions.remove(session)
            logger.debug(f"{session.session_type} session was removed")

    def is_compatible(
        self,
        session: T_SESSION,
        new_sessions: list[T_SESSION] | T_SESSION,
        logger: Logger,
    ) -> bool:
        """Compare session with new session parameters."""
        if not isinstance(new_sessions, list):
            new_sessions = [new_sessions]

        if session in self._existing_sessions:
            compatible = False
            for new_session in new_sessions:
                if new_session == session:
                    compatible = True
                    break
            return compatible
        else:
            raise SessionManagerException(self.__class__.__name__, "Unknown session")
