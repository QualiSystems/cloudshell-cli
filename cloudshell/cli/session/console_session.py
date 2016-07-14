__author__ = 'g8y3e'

from collections import OrderedDict

import re
from cloudshell.cli.session.expect_session import ExpectSession
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession


class ConsoleSession(ExpectSession):
    def __init__(self, *args, **kwargs):
        """Initiate console connection, by default open ssh to 22 port and login to console server

        :param args:
        :param kwargs: 'console_server_ip', 'console_server_user', 'console_server_password', 'console_port' mandatory'
        :return:
        """

        ExpectSession.__init__(self, None, *args, **kwargs)

        self._console_username = kwargs['console_server_user']
        self._console_password = kwargs['console_server_password']
        self._console_host = kwargs['console_server_ip']

        self._session_handler = SSHSession(self._console_username, self._console_password, self._console_host,
                                           port=22, logger=self.logger)

        self._console_port = kwargs['console_port']

    def _clear_console(self, re_string=''):
        """Disconnect console if it's used by sending 'clear line xx' command

        :param re_string:
        :return:
        """

        expect_map = OrderedDict()
        expect_map['[Pp]assword:'] = lambda: self.send_line(self._password)
        expect_map['\[confirm\]'] = lambda: self.send_line('')

        self.hardware_expect('enable', re_string=re_string, expect_map=expect_map)

        output_str = self.hardware_expect('show hosts | i {0}'.format(self._console_port), re_string=re_string,
                                          expect_map=expect_map)

        pattern_str = '{0}\s+[\d][\d]([\d][\d])\s+\(.*\).*'.format(self._console_port)
        line_number = None
        for line_str in output_str.splitlines():
            result_match = re.search(pattern_str, line_str)
            if result_match:
                line_number = result_match.group(1)
                break

        if line_number:
            self.hardware_expect('clear line {0}'.format(line_number), re_string=re_string, expect_map=expect_map)

    def _connect_to_console(self, re_string=''):
        """Open console connection

        :param re_string:
        :return:
        """

        expect_map = OrderedDict()
        expect_map['[Ll]ogin:|[Uu]sername:'] = lambda: self.send_line(self._username)
        expect_map['[Pp]assword:'] = lambda: self.send_line(self._password)
        expect_map['[Cc]onnection refused'] = lambda: (self._clear_console(re_string),
                                                       self.send_line(self.console_port))

        self.hardware_expect(self._console_port, re_string=re_string)

    def connect(self, re_string=''):
        """Open ssh or telnet connection to device

        :param re_string: expected string
        :return:
        """

        try:
            self._session_handler.connect(re_string)
            if self._console_port:
                self._connect_to_console(re_string)
        except Exception as error_object:
            if re.search('incompatible version', str(error_object).lower()) is None:
                self._session_handler = TelnetSession(self._console_username, self._console_password,
                                                      self._console_host, port=23, logger=self._logger)
                self._session_handler.connect(re_string)

                if self._console_port:
                    self._connect_to_console(re_string)
            else:
                raise error_object

    def disconnect(self):
        """Disconnect from device

        :return:
        """

        self._session_handler.disconnect()

    def _send(self, command_string):
        """Send data to device

        :param command_string: command string
        :return:
        """

        self._session_handler._send(command_string)

    def _receive(self, timeout=None):
        """Read data from device

        :param timeout: time for waiting buffer
        :return: str
        """

        self._session_handler._receive(timeout=timeout)
