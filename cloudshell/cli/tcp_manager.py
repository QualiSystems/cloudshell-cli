__author__ = 'g8y3e'

import socket

from cloudshell.cli.session_manager import SessionManager

class TCPManager(SessionManager):
    def __init__(self, *args, **kwargs):
        SessionManager.__init__(self, socket.socket(socket.AF_INET, socket.SOCK_STREAM), *args, **kwargs)

        self._buffer_size = 1024
        if 'buffer_size' in kwargs:
            self._buffer_size = kwargs['buffer_size']

        if self._port is not None:
            self._port = int(self._port)

    def connect(self, expected_str=''):
        """
            Connect to device

            :param expected_str: regular expression string
            :return:
        """
        SessionManager.connect(self, expected_str)

        server_address = (self._host, self._port)
        self._handler.connect(server_address)

        self._handler.settimeout(self._timeout)

        return self.hardware_expect('', expected_str)

    def disconnect(self):
        """
            Disconnect from device

            :return:
        """
        SessionManager.disconnect(self)
        self._handler.close()

    def _send(self, command_string):
        """
            Send data to device

            :param command_string: ommand string
            :return:
        """
        self._handler.sendall(command_string)

    def _receive(self, timeout=None):
        """
            Read data from device

            :param timeout: time for waiting buffer
            :return: str
        """
        return self._handler.recv(self._buffer_size)
