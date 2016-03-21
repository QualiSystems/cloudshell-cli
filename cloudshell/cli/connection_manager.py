__author__ = 'g8y3e'

from collections import OrderedDict, deque
from threading import Lock, Event
import time

from cloudshell.cli.helper.singleton import Singleton

from cloudshell.cli.telnet_session import TelnetSession
from cloudshell.cli.ssh_session import SSHSession
from cloudshell.cli.tcp_session import TCPSession
from cloudshell.cli.console_session import ConsoleSession

create_session_lock = Lock()

class ConnectionManager:
    __metaclass__ = Singleton

    DEFAULT_TYPE = 'auto'

    class SessionInfo:
        def __init__(self, class_def, keys=list()):
            self.class_def = class_def
            self.keys = keys

    def __init__(self, max_connections_count=4):
        self._session_pool = deque()

        self._created_session_count = 0
        self._max_connections = max_connections_count

        self._connection_map = OrderedDict()

        self._connection_map['tcp'] = self.SessionInfo(TCPSession)
        self._connection_map['console'] = self.SessionInfo(ConsoleSession,
                                                           ['console_server_ip', 'console_server_user',
                                                            'console_server_password', 'console_port'])

        self._connection_map['telnet'] = self.SessionInfo(TelnetSession)
        self._connection_map['ssh'] = self.SessionInfo(SSHSession)

        self._default_keys = ['username', 'password', 'host']

    def set_max_connections(self, max_connections_count=4):
        self._max_connections = max_connections_count

    def _check_parameters(self, connection_type, connection_parameters):
        """

        :param connection_type:
        :param connection_parameters:
        :return:
        """
        keys = self._default_keys
        if len(self._connection_map[connection_type].keys) > 0:
            keys = self._connection_map[connection_type].keys

        if connection_parameters is None:
            return False

        for key in keys:
            if key not in connection_parameters:
                return False

        return True

    def _create_session(self, connection_type, prompt, logger, connection_parameters):
        """

        :param connection_type:
        :param prompt:
        :param connection_parameters:
        :return:
        """
        session_object = None
        if self._check_parameters(connection_type, connection_parameters):
            session_object = self._connection_map[connection_type].class_def(logger=logger,
                                                                             **connection_parameters)
            session_object.connect(re_string=prompt)
        else:
            raise Exception('ConnectionManager', 'Incorrect connection parameters!')

        return session_object

    def _get_session_from_pool(self):
        retry_count = 3
        time_wait = 20
        wait_delay = 0.3

        time_counted = 0
        session_object = None

        while time_counted < (retry_count * time_wait):
            while len(self._session_pool) == 0 and time_counted < time_wait:
                time_counted += wait_delay
                time.sleep(wait_delay)

            create_session_lock.acquire()
            if len(self._session_pool) != 0:
                session_object = self._session_pool.popleft()
            create_session_lock.release()

            if not session_object is None:
                return session_object

        return session_object

    def add_session_to_pool(self, session, time=None):
        create_session_lock.acquire()
        self._session_pool.append(session)
        create_session_lock.release()

    def get_session(self, connection_type=DEFAULT_TYPE, prompt='', logger=None, **kwargs):
        """

        :param connection_type:
        :param kwargs:
        :return:
        """
        create_session_lock.acquire()
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
            self._logger.warning('Prompt is empty!')

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
                    logger.error('\n{0} connection failed: '.format(key.upper()) + 'with error msg:' + error_object.message)

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

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root', password='Password1',
                                              host='192.168.42.235', timeout=1)

    ConnectionManager().add_session_to_pool(session_object)

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root', password='Password1',
                                              host='192.168.42.235', timeout=1)

    ConnectionManager().add_session_to_pool(session_object)

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root', password='Password1',
                                              host='192.168.42.235', timeout=1)

    ConnectionManager().add_session_to_pool(session_object)

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root', password='Password1',
                                              host='192.168.42.235', timeout=1)

    ConnectionManager().add_session_to_pool(session_object)

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root', password='Password1',
                                                     host='192.168.42.235', timeout=1)

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root', password='Password1',
                                                     host='192.168.42.235', timeout=1)

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root', password='Password1',
                                                     host='192.168.42.235', timeout=1)

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root', password='Password1',
                                                     host='192.168.42.235', timeout=1)

    thread = threading.Timer(3, testThread)
    thread.start()

    session_object = ConnectionManager().get_session(prompt='[$#] *$', logger=logger, username='root', password='Password1',
                                                     host='192.168.42.235', timeout=1)

    thread.join()




