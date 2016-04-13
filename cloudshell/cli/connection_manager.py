from weakref import WeakKeyDictionary
from Queue import Queue
from threading import Lock, currentThread

import inject
import types

_CREATE_SESSION_LOCK = Lock()

_SESSION_CONTAINER = WeakKeyDictionary()


def get_thread_session():
    """Return same session for thread"""
    if not currentThread() in _SESSION_CONTAINER:
        _SESSION_CONTAINER[currentThread()] = ConnectionManager.get_session()
    return _SESSION_CONTAINER[currentThread()]


class SessionCreator(object):
    """Creator for session"""

    def __init__(self, classobj):
        """Classobj for session"""
        self.classobj = classobj
        """Classobj for proxy"""
        self.proxy = None
        """Dict that contains keys and funcs or values, used like a key dictionary when creates session object"""
        self.kwargs = None

    def create_session(self):
        """Creates session object
        :rtype: Session
        :raises: Exception
        """

        kwargs = {}
        for key in self.kwargs:
            if callable(self.kwargs[key]):
                kwargs[key] = self.kwargs[key]()
            else:
                kwargs[key] = self.kwargs[key]

        if self.classobj and isinstance(self.classobj, types.ObjectType):
            if self.proxy and isinstance(self.proxy, types.ObjectType):
                return self.proxy(self.classobj(**kwargs))
            else:
                return self.classobj(**kwargs)
        else:
            raise Exception('SessionCreator', 'Incorrect classobj for session {0}'.format(self.classobj))


class ReturnToPoolProxy(object):
    """Proxy class, return session back to pool when GC destruct session"""

    def __init__(self, instance):
        self._instance = instance

    def __getattr__(self, name):
        return getattr(self._instance, name)

    def __del__(self):
        if inject and inject.is_configured():
            cm = inject.instance('connection_manager')
            cm.return_session_to_pool(self)


class ConnectionManager(object):
    """Class implements Object Pool pattern for sessions, creates and pool sessions for specific types"""

    def __init__(self):
        self._config = inject.instance('config')
        self._connection_map = self._config.CONNECTION_MAP

        self._max_connections = self._config.SESSION_POOL_SIZE

        self._session_pool = Queue(maxsize=self._max_connections)
        self._created_session_count = 0

        self._prompt = self._config.DEFAULT_PROMPT
        self._connection_type_auto = self._config.CONNECTION_TYPE_AUTO
        self._connection_type = self._config.CONNECTION_TYPE

        self._pool_timeout = self._config.POOL_TIMEOUT
        self.logger = inject.instance('logger')
        self.logger.debug('Connection manager created')

    @inject.params(logger='logger')
    def _new_session(self, connection_type, logger=None):
        """Creates new session
        :param str connection_type:
        :rtype: Session
        :raises: Exception
        """
        if connection_type in self._connection_map:
            session_object = self._connection_map[connection_type].create_session()
            session_object.connect(re_string=self._prompt)
            logger.debug('Created new session')
        else:
            raise Exception('ConnectionManager', 'Connection type {0} have not defined'.format(connection_type))

        return session_object

    @inject.params(context='context', logger='logger', api='api')
    def _create_session_by_connection_type(self, context=None, api=None, logger=None):
        """Creates session object for connection type
        :rtype: Session
        :raises: Exception
        """

        if self._connection_type and callable(self._connection_type):
            connection_type = self._connection_type()
        elif self._connection_type and isinstance(self._connection_type, str):
            connection_type = self._connection_type
        else:
            logger.error('Connection type have not defined')
            raise Exception('_create_session_by_connection_type', 'Connection type have not defined')

        if not self._prompt or len(self._prompt) == 0:
            logger.warning('Prompt is empty!')

        logger.info('\n-------------------------------------------------------------')
        logger.info('Connection - {0}'.format(connection_type))

        session_object = None
        if connection_type != self._connection_type_auto:
            session_object = self._new_session(connection_type, context=context, api=api, logger=logger)
        else:
            for key in self._connection_map:
                logger.info('\n--------------------------------------')
                logger.info('Trying to open {0} connection ...'.format(key))
                try:
                    session_object = self._new_session(key)
                    if session_object:
                        break
                except Exception as error_object:
                    logger.error(
                        '\n{0} connection failed: '.format(key.upper()) + 'with error msg:' + error_object.message)

        if session_object is None:
            logger.error('Connection failed!')
            raise Exception('ConnectionManager', 'Cannot create session, see logs for details')

        return session_object

    @inject.params(logger='logger')
    def _get_session_from_pool(self, logger=None):
        """Take session from pool
        :rtype: Session
        :raises: Exception
        """
        try:
            session_object = self._session_pool.get(True, self._pool_timeout)
            logger.info('Get session from pool')
        except Exception as error_object:
            raise Exception('ConnectionManager', "Can't get find free session from pool!")

        return session_object

    def return_session_to_pool(self, session, time_out=None):
        """Creates session object for connection type
        :param: Session session:
        """

        if not time_out:
            time_out = self._pool_timeout
        self._session_pool.put(session, True, time_out)

    @inject.params(logger='logger')
    def get_session_instance(self, logger=None):
        """Return session object, takes it from pool or create new session
        :rtype: Session
        """

        logger.debug('Get session')

        with _CREATE_SESSION_LOCK:
            if self._session_pool.empty() and self._created_session_count < self._max_connections:
                self.return_session_to_pool(self._create_session_by_connection_type())
                self._created_session_count += 1
        return self._get_session_from_pool()

    @staticmethod
    @inject.params(connection_manager='connection_manager')
    def get_session(connection_manager=None):
        """
        :rtype: Session
        """
        return connection_manager.get_session_instance()
