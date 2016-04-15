__author__ = 'yar'
import copy
import re

from cloudshell.cli.ssh_manager import SSHManager
from cloudshell.cli.telnet_manager import TelnetManager
from cloudshell.cli.old.console_manager import ConsoleManager
from cloudshell.cli.file_manager import FileManager
from cloudshell.cli.tcp_manager import TCPManager


class ConnectionManager(object):
    CONNECTION_ORDER = ['tcp', 'console', 'telnet', 'ssh']
    CONNECTION_MAP = {'ssh': SSHManager, 'telnet': TelnetManager, 'console': ConsoleManager, 'tcp': TCPManager,
                      'file': FileManager}
    KEY_MAP = {'console': ['console_server_ip', 'console_server_user', 'console_server_password', 'console_port'],
               'file': ['filename'],
               'common': ['username', 'password', 'host']}
    PROMPT_RE = '.*>|.*#|\(config.*\)#'

    def __init__(self, connection_type='auto', logger=None, **kwargs):
        self._connection_type = connection_type.lower()
        self._logger = logger
        self._connection_order = copy.deepcopy(ConnectionManager.CONNECTION_ORDER)
        self._connection_map = copy.deepcopy(ConnectionManager.CONNECTION_MAP)
        self._key_map = copy.deepcopy(ConnectionManager.KEY_MAP)
        self._connection_params = kwargs

    def _check_params(self, conn_type):
        """
            Checking connection parameters

            :param conn_type: type oth connection string. Example: 'ssh'
            :return: bool
        """
        params = self._connection_params
        if conn_type in self._key_map.keys():
            keys = self._key_map[conn_type]
        else:
            keys = self._key_map['common']

        for key in keys:
            if key not in params.keys():
                return False
        return True

    def _generic_connection(self, conn_type, prompt):
        """
            Generic connection method

            :param conn_type:
            :param prompt:
            :return: SessionManager
        """
        connection = None
        conn_type = re.sub(' ', '', conn_type.lower())
        if self._check_params(conn_type) and conn_type in self._connection_map.keys():
            try:
                session = self._connection_map[conn_type](logger=self._logger, **self._connection_params)
                session.connect(expected_str=prompt)
                connection = session
            except Exception as err:
                error_str = str(err)
                if self._logger:
                    self._logger.error(error_str)

                raise Exception('Console Manager', error_str)
        else:
            raise Exception('Incorrect connection type')

        return connection

    def get_session(self, prompt=PROMPT_RE):
        """
            Get sessin handler

            :param prompt: regular expression string
            :return: SessionManager
        """
        connection = None
        connection_type = self._connection_type
        self._logger.info('\n-------------------------------------------------------------')
        self._logger.info('Connection - {0}'.format(self._connection_type))
        if 'host' in self._connection_params:
            self._logger.info('Host - {0}'.format(self._connection_params['host']))
        if 'port' in self._connection_params and not self._connection_params['port'] is None:
            self._logger.info('Port - {0}'.format(self._connection_params['port']))
        if connection_type.lower() != 'auto':
            connection = self._generic_connection(connection_type, prompt)
        else:
            for conn_type in self._connection_order:
                try:
                    self._logger.info('\n--------------------------------------')
                    self._logger.info('Trying to open {0} connection ...'.format(conn_type))
                    session = self._generic_connection(conn_type, prompt)
                    if session:
                        connection = session
                        break
                except Exception as e:
                    self._logger.error('\n{0} connection failed'.format(conn_type.upper()))
        if not connection:
            self._logger.error('Connection failed')
            raise Exception('Connection failed')

        self._logger.info("Connected")
        return connection
