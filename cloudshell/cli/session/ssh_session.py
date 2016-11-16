import socket
import traceback

from cloudshell.cli.session.session_exceptions import SessionException, SessionReadTimeout, SessionReadEmptyData
import paramiko
from cloudshell.cli.session.connection_params import ConnectionParams
from cloudshell.cli.session.expect_session import ExpectSession


class SSHSessionException(SessionException):
    pass


class SSHSession(ExpectSession, ConnectionParams):
    SESSION_TYPE = 'SSH'
    BUFFER_SIZE = 512

    def __init__(self, host, username, password, port=None, on_session_start=None, *args, **kwargs):
        ConnectionParams.__init__(self, host, port=port, on_session_start=on_session_start)
        ExpectSession.__init__(self, *args, **kwargs)

        if self.port is None:
            self.port = 22

        self.username = username
        self.password = password

        self._handler = None
        self._current_channel = None
        self._buffer_size = self.BUFFER_SIZE

    def __eq__(self, other):
        """
        :param other:
        :type other: SSHSession
        :return:
        """
        return ConnectionParams.__eq__(self,
                                       other) and self.username == other.username and self.password == other.password

    def __del__(self):
        self.disconnect()

    def connect(self, prompt, logger):
        """Connect to device through ssh
        :param prompt: expected string in output
        :param logger: logger
        """

        if not self._handler:
            self._handler = paramiko.SSHClient()
            self._handler.load_system_host_keys()
            self._handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self._handler.connect(self.host, self.port, self.username, self.password, timeout=self._timeout,
                                  banner_timeout=30, allow_agent=False, look_for_keys=False)
        except Exception as e:
            logger.error(traceback.format_exc())
            raise SSHSessionException(self.__class__.__name__,
                                      'Failed to open connection to device: {0}'.format(e.message))

        self._current_channel = self._handler.invoke_shell()
        self._current_channel.settimeout(self._timeout)

        self.hardware_expect(None, expected_string=prompt, timeout=self._timeout, logger=logger)
        if self.on_session_start and callable(self.on_session_start):
            self.on_session_start(self, logger)
        self._active = True

    def disconnect(self):
        """Disconnect from device
        :return:
        """

        # self._current_channel = None
        if self._handler:
            self._handler.close()
        self._active = False

    def _send(self, command, logger):
        """Send message to device

        :param data_str:  message/command
        :return:
        """

        self._current_channel.send(command)

    def _receive(self, timeout, logger):
        """Read session buffer

        :param timeout: time between retries
        :return:
        """

        # Set the channel timeout
        timeout = timeout if timeout else self._timeout
        self._current_channel.settimeout(timeout)

        try:
            data = self._current_channel.recv(self._buffer_size)
        except socket.timeout:
            raise SessionReadTimeout()

        if not data:
            raise SessionReadEmptyData()

        return data
