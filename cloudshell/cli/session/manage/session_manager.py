import logging
from typing import TYPE_CHECKING, List, Sequence

from cloudshell.cli.session.manage.exception import SessionManagerException

if TYPE_CHECKING:
    from cloudshell.cli.session.core.session import Session
    from cloudshell.cli.session.core.factory import AbstractSessionFactory

logger = logging.getLogger(__name__)


class SessionManager(object):
    def __init__(self, max_size: int = 1):
        self._existing_sessions = []
        self._max_size = max_size

    def new_session(self, factories: Sequence["AbstractSessionFactory"]) -> "Session":

        for factory in factories:
            try:
                session = factory.get_active_session()
                logger.debug(f"Created new {factory.get_session_type()} session")
                self._existing_sessions.append(session)
                return session
            except Exception:
                logger.exception(f"Unable to create session {factory.get_session_type()}.")
        raise SessionManagerException(
            f"Failed to create new session for type {', '.join(f.get_session_type() for f in factories)}, see logs for details."
        )

    def sessions_count(self):
        """Count of existing sessions.

        :rtype: int
        """
        return len(self._existing_sessions)

    def full(self):
        return self.sessions_count() >= self._max_size

    def remove_session(self, session: "Session"):
        """Remove session."""
        if session in self._existing_sessions:
            self._existing_sessions.remove(session)
            logger.debug("{} session was removed".format(session.session_type))

    def is_compatible(self, session: "Session",
                      factories: Sequence["AbstractSessionFactory"]):
        """Compare session with new session parameters."""
        if session in self._existing_sessions:
            for factory in factories:
                if factory.compatible(session):
                    return session
        else:
            raise SessionManagerException("Unknown session.")
