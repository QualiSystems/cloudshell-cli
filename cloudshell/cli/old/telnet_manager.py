__author__ = 'g8y3e'

import telnetlib

from cloudshell.cli.old.session_manager import SessionManager

class TelnetManager(SessionManager):
    def __init__(self, *args, **kwargs):
        SessionManager.__init__(self, telnetlib.Telnet(), *args, **kwargs)

        if self._port is None:
            self._port = 23

    def connect(self, expected_str=''):
        """
            Connect to device

            :param expected_str: reglar expression string
            :return:
        """
        SessionManager.connect(self, expected_str)

        self._handler.open(self._host, int(self._port), self._timeout)
        if self._handler.get_socket() is None:
            raise Exception('Telnet', 'Connect error!')

        output = self.hardware_expect('', expected_str)
        if len(output) == 0:
            raise Exception('Telnet Manager', 'Connection failed!')

        return output

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

            :param command_string: command string
            :return:
        """
        self._handler.write(command_string)

    def _receive(self, timeout=None):
        """
            Read data from device

            :param timeout: time for waiting buffer
            :return: str
        """
        if not timeout is None:
            self._handler.get_socket().settimeout(timeout)

        data = self._handler.read_some()
        return data
