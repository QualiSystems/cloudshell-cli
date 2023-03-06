import socket

from cloudshell.cli.session.connection_params import ConnectionParams
from cloudshell.cli.session.expect_session import ExpectSession


class TCPSession(ExpectSession, ConnectionParams):
    SESSION_TYPE = "TCP"
    BUFFER_SIZE = 1024

    def __init__(self, host, port, on_session_start=None, *args, **kwargs):
        ConnectionParams.__init__(
            self, host=host, port=port, on_session_start=on_session_start
        )
        ExpectSession.__init__(self, *args, **kwargs)

        self._buffer_size = self.BUFFER_SIZE
        self._handler = None

    def _initialize_session(self, prompt, logger):
        self._handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (self.host, self.port)
        self._handler.connect(server_address)

        self._handler.settimeout(self._timeout)

    def probe_for_prompt(self, expected_string, logger):
        return "DUMMY_PROMPT"

    def _connect_actions(self, prompt, logger):
        self._on_session_start(logger)

    def disconnect(self):
        """Disconnect from device/close the session."""
        self._handler.close()
        self._active = False

    def _send(self, command, logger):
        """Send message to the session.

        :param command: message/command to send
        :return:
        """
        self._handler.sendall(command)

    def _set_timeout(self, timeout):
        self._handler.settimeout(timeout)

    def _read_byte_data(self):
        pass

    def _read_str_data(self):
        return self._handler.recv(self._buffer_size)
