from Queue import Queue
import traceback
from threading import currentThread, Condition, RLock, Lock
import time
from logging import Logger

from cloudshell.cli.session.connection_manager_exceptions import SessionManagerException, ConnectionManagerException
import inject
from cloudshell.cli.helper.weak_key_dictionary_with_callback import WeakKeyDictionaryWithCallback
import cloudshell.configuration.cloudshell_cli_configuration as package_config
from cloudshell.shell.core.config_utils import call_if_callable, \
    override_attributes_from_config
from cloudshell.configuration.cloudshell_shell_core_binding_keys import CONFIG, LOGGER
from cloudshell.cli.session.session import Session


class SessionManager(object):
    """
    Create or remove session for defined connection type
    """
    CONNECTION_TYPE_AUTO = package_config.CONNECTION_TYPE_AUTO
    CONNECTION_TYPE = package_config.CONNECTION_TYPE
    CONNECTION_MAP = package_config.CONNECTION_MAP
    DEFAULT_PROMPT = package_config.DEFAULT_PROMPT
    DEFAULT_CONNECTION_TYPE = package_config.DEFAULT_CONNECTION_TYPE

    def __init__(self, logger=None, config=None, connection_map=None):
        """
        SessionManager constructor
        :param logger:
        :param config:
        :return:
        """
        self._logger = logger
        self._config = config
        self._connection_map = connection_map

        self._sessions = []
        """Override default configuration attributes"""
        overridden_config = override_attributes_from_config(SessionManager, config=self.config)
        self._connection_type_auto = overridden_config.CONNECTION_TYPE_AUTO
        self._connection_type = overridden_config.CONNECTION_TYPE
        if not self._connection_map:
            self._connection_map = overridden_config.CONNECTION_MAP
        self._prompt = overridden_config.DEFAULT_PROMPT
        self._default_connection_type = overridden_config.DEFAULT_CONNECTION_TYPE

        """Lock"""
        self._SESSION_LOCK = RLock()

    @property
    def logger(self):
        """
        Property for logger
        :rtype: Logger
        """
        return self._logger or inject.instance(LOGGER)

    @logger.setter
    def logger(self, logger):
        self._logger = logger

    @property
    def config(self):
        """
        Property for config
        :rtype: ModuleType
        """
        return self._config or inject.instance(CONFIG)

    @property
    def created_sessions(self):
        """
        Count of session was created and exist
        :rtype: int
        """
        with self._SESSION_LOCK:
            return len(self._sessions)

    def get_connection_type(self):
        """
        Connection type
        :rtype: str
        :raises: SessionManagerException
        """
        if self._connection_type and callable(self._connection_type):
            connection_type = self._connection_type()
        elif self._connection_type and isinstance(self._connection_type, str):
            connection_type = self._connection_type
        else:
            err_msg = 'Unknown connection type {0}'.format(self._connection_type)
            self.logger.error(err_msg)
            raise SessionManagerException(self.__class__.__name__, err_msg)

        if not connection_type:
            connection_type = self._default_connection_type

        return connection_type.lower()

    def _new_session(self, connection_type, prompt):
        """Creates new session
        :param str connection_type:
        :rtype: Session
        :raises: SessionManagerException
        """

        if connection_type in self._connection_map:
            try:
                session_object = self._connection_map[connection_type].create_session()
                session_object.connect(re_string=prompt)
            except Exception as exception:
                self.logger.error('Cannot create session, Exception: {0}'.format(exception))
                raise SessionManagerException(self.__class__.__name__,
                                              'Failed to open connection, see logs for more details')
            self.logger.debug('Created new session')
        else:
            err_msg = 'Connection type \'{0}\' not defined'.format(connection_type)
            self.logger.error(err_msg)
            raise SessionManagerException(self.__class__.__name__, err_msg)
        self._sessions.append(session_object)
        return session_object

    def create_session(self, connection_type=None, prompt=None):
        """Creates session object for connection type
        :rtype: Session
        :raises: SessionManagerException
        """
        if not connection_type:
            connection_type = self.get_connection_type()

        if not prompt:
            prompt = self._prompt
        if not prompt:
            self.logger.warning('Provided Prompt for the session is empty!')

        self.logger.info('\n-------------------------------------------------------------')
        self.logger.info('Connection - {0}'.format(connection_type))

        with self._SESSION_LOCK:
            session_object = None
            if connection_type != self._connection_type_auto:
                session_object = self._new_session(connection_type, prompt)
            else:
                for key in self._connection_map:
                    self.logger.info('\n--------------------------------------')
                    self.logger.info('Trying to open {0} connection ...'.format(key))
                    try:
                        session_object = self._new_session(key, prompt)
                        if session_object:
                            break
                    except Exception as error_object:
                        self.logger.error(traceback.format_exc())
                        self.logger.error(
                            '{0} connection failed with error msg: {1}'.format(key.upper(), error_object.message))

            if session_object is None:
                err_msg = 'Failed to open connection to device, see logs for more details'
                self.logger.error(err_msg)
                raise SessionManagerException(self.__class__.__name__, err_msg)

            return session_object

    def remove_session(self, session):
        """
        Remove session
        :param session: Session which needs to be removed
        :raises: SessionManagerException
        """
        with self._SESSION_LOCK:
            if session in self._sessions:
                self._sessions.remove(session)
                del session
            else:
                raise SessionManagerException(self.__class__.__name__, 'Unknown session')


class ConnectionManager(object):
    """Class implements Object Pool pattern for sessions, creates and pool sessions for specific types"""

    """Configuration attributes"""
    POOL_TIMEOUT = package_config.POOL_TIMEOUT
    SESSION_POOL_SIZE = package_config.SESSION_POOL_SIZE
    DEFAULT_SESSION_POOL_SIZE = package_config.DEFAULT_SESSION_POOL_SIZE

    """Thread session container"""
    _SESSION_CONTAINER = WeakKeyDictionaryWithCallback()

    """Create connection manager instance lock"""
    _CREATE_LOCK = Lock()

    """Connection manager instance container"""
    _INSTANCE = None

    def __init__(self, config=None, logger=None, session_manager=None, pool_manager=None):
        """
        Connection manager constructor
        :param config:
        :param logger:
        :param session_manager:
        :param pool_manager:
        :return:
        """
        """Used for unittests"""
        self._config = config
        self._logger = logger
        self._session_manager = session_manager
        self._pool_manager = pool_manager

        """Override constants with global config values"""
        overridden_config = override_attributes_from_config(ConnectionManager, config=self.config)
        self._pool_timeout = overridden_config.POOL_TIMEOUT
        self._max_pool_size = int(call_if_callable(
            overridden_config.SESSION_POOL_SIZE) or overridden_config.DEFAULT_SESSION_POOL_SIZE)

        """Session manager condition"""
        self._SESSION_CONDITION = Condition()
        self.logger.debug('Connection manager created')

    @property
    def logger(self):
        """
        Property for the logger
        :rtype: Logger
        """
        return self._logger or inject.instance(LOGGER)

    @property
    def config(self):
        """
        Property for the config
        :rtype: ModuleType
        """
        return self._config or inject.instance(CONFIG)

    @property
    def session_manager(self):
        """
        Property for session manager instance
        :rtype: SessionManager
        """
        if not self._session_manager:
            self._session_manager = SessionManager()
        return self._session_manager

    @property
    def pool_manager(self):
        """
        Property for pool manager
        :rtype: Queue
        """
        if not self._pool_manager:
            self._pool_manager = Queue(self._max_pool_size)
        return self._pool_manager

    def get_session_instance(self):
        """Return session object, takes it from pool or create new session
        :rtype: Session
        :raises: ConnectionManagerException
        """
        call_time = time.time()
        with self._SESSION_CONDITION:
            session = None
            while session is None:
                if not self.pool_manager.empty():
                    session = self.pool_manager.get(False)
                elif self.session_manager.created_sessions < self.pool_manager.maxsize:
                    session = self.session_manager.create_session()
                else:
                    self._SESSION_CONDITION.wait(self._pool_timeout)
                    if (time.time() - call_time) >= self._pool_timeout:
                        raise ConnectionManagerException(self.__class__.__name__,
                                                         'Cannot get session instance during {} sec.'.format(
                                                             self._pool_timeout))
            return session

    def return_session_instance(self, session):
        """
        Return session instance to the pool, if session is valid. Do not use any
        :param session:
        :return:
        """
        with self._SESSION_CONDITION:
            try:
                if hasattr(session, 'is_valid') and not session.is_valid():
                    self.session_manager.remove_session(session)
                else:
                    self.pool_manager.put(session)
            finally:
                self._SESSION_CONDITION.notify()

    def remove_session_instance(self, session):
        """
        Remove session
        :param session:
        :return:
        """
        with self._SESSION_CONDITION:
            self.session_manager.remove_session(session)
            self._SESSION_CONDITION.notify()

    @staticmethod
    def get_session():
        """Get session instance from connection manager instance
        :rtype: Session
        """
        connection_manager = ConnectionManager.get_instance()
        return connection_manager.get_session_instance()

    @staticmethod
    def get_thread_session():
        """
        Create or get session from pool and hold it for current thread. Return session to the pool when thread will be
        destructed
        :rtype: Session
        """

        if not currentThread() in ConnectionManager._SESSION_CONTAINER:
            session = ConnectionManager.get_session()

            def _return_to_pool_wrap(sess):
                def _return_to_pool(*args, **kwargs):
                    """
                    Return session back to the pool
                    :param args:
                    :param kwargs:
                    :return:
                    """
                    connection_manager = ConnectionManager.get_instance()
                    connection_manager.return_session_instance(sess)

                return _return_to_pool

            ConnectionManager._SESSION_CONTAINER.set(currentThread(), session, _return_to_pool_wrap(session))
        return ConnectionManager._SESSION_CONTAINER[currentThread()]

    @staticmethod
    def destroy_thread_session(session):
        """Destroy threaded session

        :param session:
        :return:
        """
        if currentThread() in ConnectionManager._SESSION_CONTAINER:
            if session == ConnectionManager._SESSION_CONTAINER[currentThread()]:
                del ConnectionManager._SESSION_CONTAINER[currentThread()]
                ConnectionManager.destroy_session(session)

    @staticmethod
    def destroy_session(session):
        """
        Destroy session instance
        :param session:
        :return:
        """
        connection_manager = ConnectionManager.get_instance()
        connection_manager.remove_session_instance(session)

    @staticmethod
    def get_instance():
        """
        Factory method for ConnectionManager singleton
        :rtype: ConnectionManager
        """
        with ConnectionManager._CREATE_LOCK:
            if not ConnectionManager._INSTANCE:
                ConnectionManager._INSTANCE = ConnectionManager()
            return ConnectionManager._INSTANCE
