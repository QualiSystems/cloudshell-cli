import socket

from cloudshell.cli.session.expect_session import ExpectSession


class TCPSession(ExpectSession):
    SESSION_TYPE = 'TCP'

    def __init__(self, *args, **kwargs):
        ExpectSession.__init__(self, socket.socket(socket.AF_INET, socket.SOCK_STREAM), *args, **kwargs)

        self._buffer_size = 1024
        if 'buffer_size' in kwargs:
            self._buffer_size = kwargs['buffer_size']

        if self._port is not None:
            self._port = int(self._port)

    def connect(self, prompt, logger):
        """
        Open connection to device / create session
        :param prompt:
        :param logger:
        :return:
        """

        server_address = (self._host, self._port)
        self._handler.connect(server_address)

        self._handler.settimeout(self._timeout)
        output = self.hardware_expect(command=None, expected_string=prompt, logger=logger)
        self.logger.info(output)

        return output

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

        data = self._handler.recv(self._buffer_size)
        return data
