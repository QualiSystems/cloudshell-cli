from Queue import Queue
from threading import Condition
import time

from cloudshell.cli.cli_exception import CliException
from cloudshell.cli.cli_session_factory import CLISessionFactory
from cloudshell.cli.session_factory import SessionFactory
from cloudshell.cli.session_pool import SessionPool
from cloudshell.cli.session.session import Session


class SessionPoolException(CliException):
    """
    Session pool exception
    """
    pass


class SessionPoolManager(SessionPool):
    """
    Implementation of session pool
    """
    """Max count of sessions can be created"""
    MAX_POOL_SIZE = 1
    """Waiting session timeout"""
    POOL_TIMEOUT = 100

    def __init__(self, session_factory=CLISessionFactory(), max_pool_size=MAX_POOL_SIZE,
                 pool_timeout=POOL_TIMEOUT):
        """
        :param session_factory:
        :type session_factory: SessionFactory
        :param max_pool_size:
        :type max_pool_size: int
        :param pool_timeout:
        :type pool_timeout: int
        """
        self._session_condition = Condition()
        self._session_factory = session_factory
        self._max_pool_size = max_pool_size
        self._pool_timeout = pool_timeout
        self._created_sessions = []

        self._pool = Queue(self._max_pool_size)

    @property
    def created_sessions(self):
        """
        Created session count
        :rtype: int
        """
        return len(self._created_sessions)

    def get_session(self, session_type, connection_attrs, prompt, logger):
        """Return session object, takes it from pool or create new session
        :param logger:
        :type logger: Logger
        :param session_args: Session arguments
        :type session_args: dict
        :rtype: Session
        :raises: ConnectionManagerException
        """
        call_time = time.time()
        with self._session_condition:
            session_obj = None
            while session_obj is None:
                if not self._pool.empty():
                    session_obj = self._get_from_pool(session_type, connection_attrs, prompt, logger)
                elif self.created_sessions < self._pool.maxsize:
                    session_obj = self._new_session(session_type, connection_attrs, prompt, logger)
                else:
                    self._session_condition.wait(self._pool_timeout)
                    if (time.time() - call_time) >= self._pool_timeout:
                        raise SessionPoolException(self.__class__.__name__,
                                                   'Cannot get session instance during {} sec.'.format(
                                                       self._pool_timeout))
            return session_obj

    def remove_session(self, session, logger):
        """
        Remove session from the pool
        :param session:
        :type session: Session
        :param logger:
        :type logger: Logger
        """
        logger.debug('Removing session')
        with self._session_condition:
            if session in self._created_sessions:
                self._created_sessions.remove(session)
                self._session_condition.notify()

    def return_session(self, session, logger):
        """
        Return session back to the pool
        :param session:
        :type session: Session
        :param logger:
        :type logger: Logger
        """
        logger.debug('Return session to the pool')
        with self._session_condition:
            session.new_session = False
            try:
                if hasattr(session, 'is_valid') and not session.is_valid():
                    self.remove_session(session, logger)
                else:
                    self._pool.put(session)
            finally:
                self._session_condition.notify()

    def _new_session(self, session_type, connection_attrs, prompt, logger):
        """
        Create new session using session factory
        :param logger:
        :param session_args:
        :type session_args: dict
        """
        logger.debug('Creating new session')

        session = self._session_factory.new_session(session_type, connection_attrs, prompt, logger)
        session.connection_attrs = connection_attrs
        session.new_session = True
        self._created_sessions.append(session)
        return session

    def _get_from_pool(self, session_type, connection_attrs, prompt, logger):
        """
        Get session from the pool
        :param logger:
        :param session_args:
        :type session_args: dict
        """
        logger.debug('getting session from the pool')
        session = self._pool.get(False)
        if session.connection_attrs != connection_attrs or not isinstance(session, session_type):
            logger.debug('Session args was changed, creating session with new args')
            self.remove_session(session, logger)
            session = self._new_session(session_type, connection_attrs, prompt, logger)
        return session
