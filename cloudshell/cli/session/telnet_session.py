__author__ = 'g8y3e'

import telnetlib
import inject
from collections import OrderedDict
from cloudshell.cli.session.expect_session import ExpectSession
from cloudshell.configuration.cloudshell_shell_core_binding_keys import LOGGER


class TelnetSession(ExpectSession):
    def __init__(self, *args, **kwargs):
        ExpectSession.__init__(self, telnetlib.Telnet(), *args, **kwargs)

        if self._port is None:
            self._port = 23

    @inject.params(logger=LOGGER)
    def connect(self, re_string='', logger=None):
        """
            Connect to device

            :param re_string: regular expression string
            :return:
        """

        self._handler.open(self._host, int(self._port), self._timeout)
        if self._handler.get_socket() is None:
            raise Exception('TelnetSession', "Can't connect to device!")

        expect_map = OrderedDict()
        expect_map['[Ll]ogin:|[Uu]ser:'] = lambda session: session.send_line(session._username)
        expect_map['[Pp]assword:'] = lambda session: session.send_line(session._password)

        out = self.hardware_expect(re_string=re_string, expect_map=expect_map)
        self._default_actions()
        logger.info(out)

        return out

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
