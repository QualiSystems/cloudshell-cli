import time
from threading import Condition

from cloudshell.cli.service.cli_exception import CliException
from cloudshell.cli.service.session_manager_impl import SessionManagerImpl
from cloudshell.cli.service.session_pool import SessionPool

try:
    from queue import Queue
except ImportError:
    from Queue import Queue


class SessionPoolException(CliException):
    """Session pool exception."""


class SessionPoolManager(SessionPool):
    """Implementation of session pool."""

    """Max count of sessions can be created"""
    MAX_POOL_SIZE = 1
    """Waiting session timeout"""
    POOL_TIMEOUT = 100

    def __init__(
        self,
        session_manager=SessionManagerImpl(),
        max_pool_size=MAX_POOL_SIZE,
        pool_timeout=POOL_TIMEOUT,
        pool=None,
    ):
        """Initialize Session pool manager.

        :param session_manager:
        :type session_manager: SessionManagerImpl
        :param max_pool_size:
        :type max_pool_size: int
        :param pool_timeout:
        :type pool_timeout: int
        """
        self._session_condition = Condition()
        self._session_manager = session_manager
        self._max_pool_size = max_pool_size
        self._pool_timeout = pool_timeout

        self._pool = pool or Queue(self._max_pool_size)

    def get_session(self, defined_sessions, prompt, logger):
        """Return session object, takes it from pool or create new session.

        :param collections.Iterable defined_sessions:
        :param prompt:
        :param logger:
        :return:
        :rtype: Session
        """
        call_time = time.time()
        with self._session_condition:
            session_obj = None
            while session_obj is None:
                if not self._pool.empty():
                    session_obj = self._get_from_pool(defined_sessions, prompt, logger)
                elif (
                    self._session_manager.existing_sessions_count() < self._pool.maxsize
                ):
                    session_obj = self._new_session(defined_sessions, prompt, logger)
                else:
                    self._session_condition.wait(self._pool_timeout)
                    if (time.time() - call_time) >= self._pool_timeout:
                        raise SessionPoolException(
                            self.__class__.__name__,
                            "Cannot get session instance during {} sec.".format(
                                self._pool_timeout
                            ),
                        )
            return session_obj

    def remove_session(self, session, logger):
        """Remove session from the pool.

        :param session:
        :type session: cloudshell.cli.session.session.Session
        :param logger:
        :type logger: Logger
        """
        logger.debug("Removing session")
        with self._session_condition:
            self._session_manager.remove_session(session, logger)
            self._session_condition.notify()

    def return_session(self, session, logger):
        """Return session back to the pool.

        :param session:
        :type session: cloudshell.cli.session.session.Session
        :param logger:
        :type logger: Logger
        """
        logger.debug("Return session to the pool")
        with self._session_condition:
            session.new_session = False
            self._pool.put(session)
            self._session_condition.notify()

    def _new_session(self, new_sessions, prompt, logger):
        """Create new session using session manager.

        :param new_sessions
        :param prompt:
        :param logger:
        :return:
        """
        logger.debug("Creating new session")
        session = self._session_manager.new_session(new_sessions, prompt, logger)
        session.new_session = True
        return session

    def _get_from_pool(self, new_sessions, prompt, logger):
        """Get session from the pool.

        :param new_sessions
        :param prompt:
        :param logger:
        :return:
        """
        logger.debug("getting session from the pool")
        session = self._pool.get(False)

        if not self._session_manager.is_compatible(session, new_sessions, logger):
            logger.debug("Session args was changed, creating session with new args")
            self.remove_session(session, logger)
            session = self._new_session(new_sessions, prompt, logger)
        return session
