__author__ = 'g8y3e'

import socket

from cloudshell.cli.session.expect_session import ExpectSession


class TCPSession(ExpectSession):
    def __init__(self, *args, **kwargs):
        ExpectSession.__init__(self, socket.socket(socket.AF_INET, socket.SOCK_STREAM), *args, **kwargs)

        self.session_type = 'TCP'
        self._buffer_size = 1024
        if 'buffer_size' in kwargs:
            self._buffer_size = kwargs['buffer_size']

        if self._port is not None:
            self._port = int(self._port)



    def connect(self, re_string=''):
        """Open connection to device / create session

        :param re_string: expected message from device
        :return:
        """

        server_address = (self._host, self._port)
        self._handler.connect(server_address)

        self._handler.settimeout(self._timeout)
        output = self.hardware_expect(re_string=re_string)
        self._logger.info(output)

        return output

    def disconnect(self):
        """Disconnect from device/close the session

        :return:
        """

        self._handler.close()

    def _send(self, data_str):
        """Send message to the session

        :param data_str: message/command to send
        :return:
        """

        self._handler.sendall(data_str)

    def _receive(self, timeout=None):
        """Read session buffer

        :param timeout:
        :return:
        """

        timeout = timeout if timeout else self._timeout
        self._handler.settimeout(timeout)

        data = self._handler.recv(self._buffer_size)
        return data
