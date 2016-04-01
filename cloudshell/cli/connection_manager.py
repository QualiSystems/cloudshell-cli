__author__ = 'g8y3e'

from Queue import Queue
from threading import Lock

import inject
from cloudshell.cli.helper.singleton import Singleton

create_session_lock = Lock()


class SessionCreator:
    def __init__(self, classobj):
        self.classobj = classobj
        self.kwargs = None

    def create_session(self, context=None, api=None):
        kwargs = {}
        for key in self.kwargs:
            if callable(self.kwargs[key]):
                kwargs[key] = self.kwargs[key](context, api)
            else:
                kwargs[key] = self.kwargs[key]
        return self.classobj(**kwargs)


class ConnectionManager:
    __metaclass__ = Singleton

    CONNECTION_TYPE_AUTO = 'auto'

    def __init__(self):

        self._config = inject.instance('config')
        self._connection_map = self._config.CONNECTION_MAP

        self._max_connections = self._config.SESSION_POOL_SIZE

        self._session_pool = Queue(maxsize=self._max_connections)
        self._created_session_count = 0

        self._prompt = self._config.DEFAULT_PROMPT
        self._default_connection_type = self._config.DEFAULT_CONNECTION_TYPE

        self._pool_timeout = self._config.POOL_TIMEOUT


        # self._default_keys = ['username', 'password', 'host']

    # def set_max_connections(self, max_connections_count=4):
    #     self._max_connections = max_connections_count

    # def _check_parameters(self, connection_type, connection_parameters):
    #     """
    #
    #     :param connection_type:
    #     :param connection_parameters:
    #     :return:
    #     """
    #     keys = self._default_keys
    #     if len(self._connection_map[connection_type].keys) > 0:
    #         keys = self._connection_map[connection_type].keys
    #
    #     if connection_parameters is None:
    #         return False
    #
    #     for key in keys:
    #         if key not in connection_parameters:
    #             return False
    #
    #     return True

    @inject.param(context='context', api='api', logger='logger')
    def _create_session(self, connection_type, logger=None, context=None, api=None):
        """

        :param connection_type:
        :param prompt:
        :param connection_parameters:
        :return:
        """
        if connection_type in self._connection_map:
            session_object = self._connection_map[connection_type].create_session(context, api)
            session_object.connect(re_string=self._prompt)
        else:
            raise Exception('ConnectionManager', 'Connection type {0} not defined'.format(connection_type))

        return session_object

    def _get_session_from_pool(self):
        try:
            session_object = self._session_pool.get(True, self._pool_timeout)
        except Exception as error_object:
            raise Exception('ConnectionManager', "Can't get find free session in pool!")
            # retry_count = 3
            # time_wait = 20
            # wait_delay = 0.3

            # time_counted = 0
            # session_object = None

            # while time_counted < (retry_count * time_wait):
            #    while len(self._session_pool) == 0 and time_counted < time_wait:
            #        time_counted += wait_delay
            #        time.sleep(wait_delay)

            #    create_session_lock.acquire()
            #    if len(self._session_pool) != 0:
            #        session_object = self._session_pool.popleft()
            #    create_session_lock.release()

            #    if not session_object is None:
            #        return session_object

        return session_object

    def add_session_to_pool(self, session, time=None):
        self._session_pool.put(session, True, self._pool_timeout)
        # create_session_lock.acquire()
        # self._session_pool.append(session)
        # create_session_lock.release()

    @inject.params(logger='logger', context='context')
    def get_session(self, connection_type=None, prompt='', logger=None, **kwargs):
        """

        :param connection_type:
        :param kwargs:
        :return:
        """

        if not connection_type:
            connection_type = self._default_connection_type

        create_session_lock.acquire()
        # if self._session_pool.empty():


        if self._created_session_count == self._max_connections:
            create_session_lock.release()
            return self._get_session_from_pool()
        else:
            self._created_session_count += 1
            create_session_lock.release()

        connection_parameters = kwargs
        connection_type = connection_type.lower()
        if (connection_type != ConnectionManager.DEFAULT_TYPE) and \
                (connection_type not in self._connection_map):
            raise Exception('ConnectionManager', 'Wrong connection type: "' + connection_type + '"!')

        if len(prompt) == 0:
            logger.warning('Prompt is empty!')

        logger.info('\n-------------------------------------------------------------')
        logger.info('Connection - {0}'.format(connection_type))

        session_object = None

        if connection_type != ConnectionManager.DEFAULT_TYPE:
            session_object = self._create_session(connection_type, prompt, logger, connection_parameters)
        else:
            for key in self._connection_map:
                logger.info('\n--------------------------------------')
                logger.info('Trying to open {0} connection ...'.format(key))
                try:
                    session_object = self._create_session(key, prompt, logger, connection_parameters)
                    if session_object:
                        break
                except Exception as error_object:
                    logger.error(
                        '\n{0} connection failed: '.format(key.upper()) + 'with error msg:' + error_object.message)

        if session_object is None:
            logger.error('Connection failed!')
            raise Exception('ConnectionManager', 'Connection failed!')

        return session_object


if __name__ == "__main__":
    import threading

    session_object = None


    def testThread():
        ConnectionManager().add_session_to_pool(session_object)


    from cloudshell.core.logger.qs_logger import get_qs_logger

    logger = get_qs_logger()

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root',
                                                     password='Password1',
                                                     host='192.168.42.235', timeout=1)

    ConnectionManager().add_session_to_pool(session_object)

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root',
                                                     password='Password1',
                                                     host='192.168.42.235', timeout=1)

    ConnectionManager().add_session_to_pool(session_object)

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root',
                                                     password='Password1',
                                                     host='192.168.42.235', timeout=1)

    ConnectionManager().add_session_to_pool(session_object)

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root',
                                                     password='Password1',
                                                     host='192.168.42.235', timeout=1)

    ConnectionManager().add_session_to_pool(session_object)

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root',
                                                     password='Password1',
                                                     host='192.168.42.235', timeout=1)

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root',
                                                     password='Password1',
                                                     host='192.168.42.235', timeout=1)

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root',
                                                     password='Password1',
                                                     host='192.168.42.235', timeout=1)

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root',
                                                     password='Password1',
                                                     host='192.168.42.235', timeout=1)

    thread = threading.Timer(3, testThread)
    thread.start()

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root',
                                                     password='Password1',
                                                     host='192.168.42.235', timeout=1)

    thread.join()
