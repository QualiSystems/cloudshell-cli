__author__ = 'g8y3e'

from Queue import Queue
from threading import Lock

import inject
from cloudshell.cli.helper.singleton import Singleton
import types

_CREATE_SESSION_LOCK = Lock()


class SessionCreator(object):
    def __init__(self, classobj):
        self.classobj = classobj
        self.proxy = None
        self.kwargs = None

    def create_session(self, context=None, api=None):
        kwargs = {}
        for key in self.kwargs:
            if callable(self.kwargs[key]):
                kwargs[key] = self.kwargs[key](context, api)
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
    def __init__(self, instance):
        self._instance = instance

    def __getattr__(self, name):
        return getattr(self._instance, name)

    def __del__(self):
        if ConnectionManager.is_defined():
            print('Run Session Deleted')
            cm = ConnectionManager()
            print(cm)
            cm.return_session_to_pool(self)


class ConnectionManager(Singleton):
    def __init__(self):

        self._config = inject.instance('config')
        self._connection_map = self._config.CONNECTION_MAP

        self._max_connections = self._config.SESSION_POOL_SIZE

        self._session_pool = Queue(maxsize=self._max_connections)
        self._created_session_count = 0

        self._prompt = self._config.DEFAULT_PROMPT
        self._default_connection_type = self._config.DEFAULT_CONNECTION_TYPE
        self._connection_type_auto = self._config.CONNECTION_TYPE_AUTO
        self._connection_type = self._config.CONNECTION_TYPE

        self._pool_timeout = self._config.POOL_TIMEOUT

    def _new_session(self, connection_type, logger=None, context=None, api=None):
        """

        :param connection_type:
        :param prompt:
        :param connection_parameters:
        :return:
        """
        if connection_type in self._connection_map:
            session_object = self._connection_map[connection_type].create_session(context, api)
            session_object.connect(re_string=self._prompt)
            logger.info('Created new session')
        else:
            raise Exception('ConnectionManager', 'Connection type {0} have not defined'.format(connection_type))

        return session_object

    @inject.params(context='context', logger='logger', api='api')
    def _create_session_by_connection_type(self, context=None, api=None, logger=None):

        if self._connection_type and callable(self._connection_type):
            connection_type = self._connection_type(context=context, api=api)
        elif self._connection_type and isinstance(self._connection_type, str):
            connection_type = self._connection_type
        else:
            connection_type = self._default_connection_type

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
                    session_object = self._new_session(connection_type, context=context, api=api, logger=logger)
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
        try:
            print('waiting for session')
            session_object = self._session_pool.get(True, self._pool_timeout)
            logger.info('Get session from pool')
        except Exception as error_object:
            raise Exception('ConnectionManager', "Can't get find free session from pool!")

        return session_object

    @inject.params(logger='logger')
    def return_session_to_pool(self, session, time_out=None, logger=None):
        if not time_out:
            time_out = self._pool_timeout
        self._session_pool.put(session, True, time_out)
        logger.info('Return session back to pool')

    def get_session_instance(self, logger=None):
        """

        :param connection_type:
        :param kwargs:
        :return:
        """

        with _CREATE_SESSION_LOCK:
            if self._session_pool.empty() and self._created_session_count < self._max_connections:
                session = self._create_session_by_connection_type()
                self._created_session_count += 1
            else:
                session = self._get_session_from_pool()
        return session

    @staticmethod
    def get_session():
        cm = ConnectionManager()
        print(cm)
        return cm.get_session_instance()
