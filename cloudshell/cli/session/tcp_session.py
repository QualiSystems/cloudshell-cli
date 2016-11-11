import socket

from cloudshell.cli.session.connection_params import ConnectionParams
from cloudshell.cli.session.expect_session import ExpectSession
from cloudshell.cli.session.session_exceptions import SessionReadTimeout, SessionReadEmptyData


class TCPSession(ExpectSession, ConnectionParams):
    SESSION_TYPE = 'TCP'
    BUFFER_SIZE = 1024

    def __init__(self, host, port, on_session_start=None):
        ConnectionParams.__init__(self, host=host, port=port, on_session_start=on_session_start)

        self._buffer_size = self.BUFFER_SIZE
        self._handler = None
        self._active = False

    def connect(self, prompt, logger):
        """
        Open connection to device / create session
        :param prompt:
        :param logger:
        :return:
        """

        self._handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (self.host, self.port)
        self._handler.connect(server_address)

        self._handler.settimeout(self._timeout)
        output = self.hardware_expect(command=None, expected_string=prompt, logger=logger)
        if self.on_session_start and callable(self.on_session_start):
            self.on_session_start(self, logger)
        self._active = True

    def disconnect(self):
        """Disconnect from device/close the session

        :return:
        """

        self._handler.close()

    def _send(self, command, logger):
        """Send message to the session

        :param command: message/command to send
        :return:
        """

        self._handler.sendall(command)

    def _receive(self, timeout, logger):
        """Read session buffer

        :param timeout:
        :return:
        """

        timeout = timeout if timeout else self._timeout
        self._handler.settimeout(timeout)

        try:
            data = self._handler.recv(self._buffer_size)
        except socket.timeout:
            raise SessionReadTimeout()

        if not data:
            raise SessionReadEmptyData()

        return data
