import logging
import time
from queue import Queue, Empty
from threading import Condition
from typing import Optional, TYPE_CHECKING, Sequence

from cloudshell.cli.session.manage.exception import SessionPoolException
from cloudshell.cli.session.manage.reconnect import reconnect
from cloudshell.cli.session.manage.session_manager import SessionManager

if TYPE_CHECKING:
    from cloudshell.cli.session.core.factory import SessionFactory
    from cloudshell.cli.session.core.session import Session

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

    def get_session(self, factories: Sequence["SessionFactory"]):
        """Return session object, takes it from pool or create new session."""
        call_time = time.time()
        with self._session_condition:
            session_obj = None
            while session_obj is None:
                session_obj = self._get_from_pool(factories)
                if session_obj:
                    continue

                elif not self._session_manager.full():
                    session_obj = self._create_session(factories)
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
            if session.get_active():
                self._pool.put(session)
            self._session_condition.notify()

    def _create_session(self, factories: Sequence["SessionFactory"]):
        """Create new session using session manager."""
        logger.debug("Creating new session")
        session = self._session_manager.new_session(factories)
        return session

    def _get_from_pool(self, factories: Sequence["SessionFactory"]) -> Optional["Session"]:
        """Get session from the pool."""
        logger.debug("Getting session from the pool")
        while True:
            try:
                session = self._pool.get_nowait()
            except Empty:
                return

            if session and self._session_manager.is_compatible(session, factories):
                if not session.get_active():
                    try:
                        reconnect(session)
                    except Exception:
                        self.remove_session(session)
                        return
                return session
