__author__ = 'g8y3e'

import telnetlib
from collections import OrderedDict

from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.cli.session.expect_session import ExpectSession


class TelnetSession(ExpectSession):
    def __init__(self, *args, **kwargs):
        ExpectSession.__init__(self, telnetlib.Telnet(), *args, **kwargs)

        if self._port is None:
            self._port = 23

    def connect(self, re_string=''):
        """
            Connect to device

            :param expected_str: regular expression string
            :return:
        """

        self._handler.open(self._host, int(self._port), self._timeout)
        if self._handler.get_socket() is None:
            raise Exception('TelnetSession', "Can't connect to device!")

        expect_map = OrderedDict()
        expect_map['[Ll]ogin:|[Uu]ser:'] = lambda: self.send_line(self._username)
        expect_map['[Pp]assword:'] = lambda: self.send_line(self._password)

        output = self.hardware_expect(re_string=re_string, expect_map=expect_map)
        self._logger.info(output)

        return output

    def disconnect(self):
        """
            Disconnect from device

            :return:
        """
        self._handler.close()

    def _send(self, data_str):
        """
            Send data to device

            :param data_str: command string
            :return:
        """
        self._handler.write(data_str)

    def _receive(self, timeout=None):
        """
            Read data from device

            :param timeout: time for waiting buffer
            :return: str
        """
        timeout = timeout if timeout else self._timeout
        self._handler.get_socket().settimeout(timeout)

        data = self._handler.read_some()
        return data

if __name__ == "__main__":
    logger = get_qs_logger()

    session = TelnetSession(username='root', password='Password1', host='192.168.42.235', logger=logger, timeout=1)
    #session = TelnetSession(username='klop', password='azsxdc', host='192.168.42.193', logger=logger, timeout=2)

    prompt = '[$#>] *$'

    session.connect(prompt)

    actions = OrderedDict()
    actions["--[Mm]ore--"] = lambda: session.send_line('')
    actions["[Pp]assword:"] = lambda: session.send_line('Password1')

    output = session.hardware_expect('enable', re_string=prompt, expect_map=actions)
    output = output

