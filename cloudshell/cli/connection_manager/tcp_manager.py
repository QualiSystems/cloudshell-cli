__author__ = 'g8y3e'

import traceback
import socket

from qualipy.common.libs.connection_manager.session_manager import SessionManager


class TCPManager(SessionManager):
    def __init__(self, *args, **kwargs):
        SessionManager.__init__(self, socket.socket(socket.AF_INET, socket.SOCK_STREAM), *args, **kwargs)

        self._buffer_size = 1024
        if 'buffer_size' in kwargs:
            self._buffer_size = kwargs['buffer_size']

        if self._port is None:
            self._port = 88
        else:
            self._port = int(self._port)

    def connect(self, expected_str=''):
        SessionManager.connect(self, expected_str)

        #try:
        server_address = (self._host, self._port)
        self._handler.connect(server_address)

        self._handler.settimeout(self._timeout)

        data = self.hardwareExpect('', expected_str)

        return data

    def disconnect(self):
        SessionManager.disconnect(self)
        self._handler.close()

    def _send(self, command_string):
        self._handler.sendall(command_string)

    def _receive(self, timeout=None):
        data = self._handler.recv(self._buffer_size)
        return data
