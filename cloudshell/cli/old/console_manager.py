author = 'g8y3e'

import re

from cloudshell.cli.session_manager import SessionManager
from cloudshell.cli.ssh_manager import SSHManager
from cloudshell.cli.old.telnet_manager import TelnetManager

class ConsoleManager(SessionManager):
    def __init__(self, *args, **kwargs):
        """
            Initiate console connection, by default open ssh to 22 port and login to console server

            :param args:
            :param kwargs:  'console_server_ip', 'console_server_user', 'console_server_password', 'console_port' mandatory
            :rtype:
        """
        SessionManager.__init__(self, None, *args, **kwargs)

        if not 'console_server_ip' in kwargs or \
                not 'console_server_user' in kwargs or \
                not 'console_server_password' in kwargs or \
                not 'console_port' in kwargs:
            raise Exception('Console Manager', 'Mandatory argument is missing.')
        else:
            self._console_username = kwargs['console_server_user']
            self._console_password = kwargs['console_server_password']
            self._console_host = kwargs['console_server_ip']

            if (len(self._console_username) > 0) and (len(self._console_password) > 0) \
                    and (len(self._console_password) > 0):

                self._session_handler = SSHManager(self._console_username, self._console_password, self._console_host,
                                                   port=22, display=True, logger=self._logger)
                self.console_port = kwargs['console_port']

            else:
                self._session_handler = None
                err_msg = 'Unable to open Console connection. One of the following parameters is empty: '
                err_msg += '[console_server_ip, console_server_user, console_server_password, console_port]'
                raise Exception('Console Manager', err_msg)

    def __del__(self):
        self.disconnect()

    def connect(self, expected_str=''):
        """
            Connect to device through ssh or telnet connection

            :param expected_str: regular expression string
            :return:
        """
        if self._session_handler is None:
            return

        try:
            self._session_handler.connect(expected_str)
            if self.console_port:
                self.connect_to_console(expected_str)

        except Exception as error:
            if str(error).find("Incompatible version") != -1:
                self._session_handler = TelnetManager(self._console_username, self._console_password,
                                                      self._console_host, port=23, display=True, logger=self._logger)
                self._session_handler.connect(expected_str)

                if self.console_port:
                    self.connect_to_console(expected_str)
            else:
                raise error

    def connect_to_console(self, expected_str):
        """
            Connect to console

            :param expected_str: regular expression string
            :return: str
        """
        expect_list = ['[Ll]ogin:', '[Uu]sername:', '[Pp]assword:',
                       'Connection refused', expected_str, 'More']

        self.send_line(self.console_port)
        out = ''
        for retry in range(18):
            ex_out = self.expect(expect_list)
            if ex_out != -1:
                i = ex_out[0]
                out = ex_out[1]
            self._logger.info(out)

            if i == 0 or i == 1:
                self.send_line(self._username)
            elif i == 2:
                self.send_line(self._password + '\n')
            elif i == 3:
                self.clear_console(self.console_port, self._password)
                self.send_line(self.console_port)
            elif i == SSHManager.TIMEOUT_ERR:
                self._logger.error('gor timeout, retrying ...')
                self.send_line(self.console_port)

            elif i == 5:
                self.send_line('')
            elif i == -1:
                self.send_line('')
            else:
                self.send_line('term len 0')
                out = self.expect(expect_list)
                self._logger.info(out)
                break

        return out

    def disconnect(self):
        """
            Disconnect from the device

            :return:
        """
        if not self._session_handler is None:
            self._session_handler.disconnect()

    def reconnect(self, expected_str, retries_count=5, sleep_time=15):
        """
            Reconnect to the device

            :param expected_str:  regular expression string
            :param retries_count: count of connect retries
            :param sleep_time: time sleeping between tries
            :return:
        """
        self._session_handler.reconnect(expected_str)

    #fixme private method
    def clear_console(self, port, password):
        """
            Use 'clear line' command in enable mode to clear console that's busy

            :param port: console port
            :param password: enable password
            :return:
        """

        out = ''
        line_number = None
        clear_done = False

        expect_list = ['\[OK\]', '[Pp]assword', '.*[>#]', '\[confirm\]']
        self.send_line('enable')

        #fixme magic numbers
        for retry in range(10):
            ex_out = self.expect(expect_list)
            i = ex_out[0]
            out += ex_out[1]

            if i == 1:
                self.send_line(password)

            elif i == 2:
                if clear_done:
                    break

                self.send_line('show hosts | i {0}'.format(port))
                out += self.expect(expect_list)[1]

                for line in out.splitlines():
                    pattern_str = '{0}\s+[\d][\d]([\d][\d])\s+\(.*\).*'.format(port)
                    res = re.search(pattern_str, out)
                    if res:
                        line_number = res.group(1)
                        break
                if line_number:
                    self.send_line('clear line {0}'.format(line_number))

            elif i == 3:
                self.send_line('\n')
                clear_done = True
            elif i == 0:
                break
        #fixme getter for logger
        self._logger.info(out)

        return 0

    def send_line(self, send_string):
        """
            Sending data to the device

            :param send_string: data string buffer
            :return: str
        """
        return self._session_handler.send_line(send_string)

    #fixme gettter for session handler
    def expect(self, re_strings='', timeout=None):
        """
            Expect method for output buffer from device

            :param re_strings: regular expression string
            :param timeout: time for waiting all buffer
            :return: str
        """
        return self._session_handler.expect(re_strings, timeout)
