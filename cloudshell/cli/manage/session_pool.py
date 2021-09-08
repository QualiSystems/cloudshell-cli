import logging
import time
from queue import Queue, Empty
from threading import Condition
from typing import Optional, List, TYPE_CHECKING

from cloudshell.cli.manage.exception import SessionPoolException
from cloudshell.cli.manage.session_manager import SessionManager

if TYPE_CHECKING:
    from cloudshell.cli.session.core.factory import AbstractSessionFactory
    from cloudshell.cli.session.core.session import Session
    from cloudshell.cli.session.prompt.prompt import Prompt

logger = logging.getLogger(__name__)


class SessionPoolManager(object):
    """Implementation of session pool."""

    """Max count of sessions can be created"""
    MAX_POOL_SIZE = 1
    """Waiting session timeout"""
    POOL_TIMEOUT = 100

    def __init__(
            self,
            session_manager: Optional[SessionManager] = None,
            max_pool_size: int = MAX_POOL_SIZE,
            pool_timeout: int = POOL_TIMEOUT,
            pool: Optional[Queue] = None,
    ):
        """Initialize Session pool manager."""
        self._session_condition = Condition()
        self._session_manager = session_manager or SessionManager()
        self._max_pool_size = max_pool_size
        self._pool_timeout = pool_timeout

        self._pool: Queue["Session"] = pool or Queue(self._max_pool_size)

    def get_session(self, factories: List["AbstractSessionFactory"],
                    prompt: Optional["Prompt"] = None):
        """Return session object, takes it from pool or create new session."""
        call_time = time.time()
        with self._session_condition:
            session_obj = None
            while session_obj is None:
                session_obj = self._get_from_pool(factories)

                if not session_obj and self._session_manager.sessions_count() < self._pool.maxsize:
                    session_obj = self._create_session(factories, prompt)
                else:
                    self._session_condition.wait(self._pool_timeout)
                    if (time.time() - call_time) >= self._pool_timeout:
                        raise SessionPoolException(
                            "Cannot get session instance during {} sec.".format(
                                self._pool_timeout
                            ),
                        )
            return session_obj

    def remove_session(self, session: "Session"):
        """Remove session from the pool."""
        logger.debug("Removing session")
        with self._session_condition:
            self._session_manager.remove_session(session)
            self._session_condition.notify()

    def return_session(self, session: "Session"):
        """Return session back to the pool."""
        logger.debug("Return session to the pool")
        with self._session_condition:
            self._pool.put(session)
            self._session_condition.notify()

    def _create_session(self, factories: List["AbstractSessionFactory"],
                        prompt: Optional["Prompt"] = None):
        """Create new session using session manager."""
        logger.debug("Creating new session")
        session = self._session_manager.new_session(factories, prompt)
        return session

    def _get_from_pool(self, factories: List["AbstractSessionFactory"]) -> Optional["Session"]:
        """Get session from the pool."""
        logger.debug("Getting session from the pool")
        while True:
            try:
                session = self._pool.get_nowait()
            except Empty:
                return

            if self._session_manager.is_compatible(session, factories) and session.get_active():
                return session

            self.remove_session(session)
