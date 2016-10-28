import telnetlib
from collections import OrderedDict

from cloudshell.cli.session.expect_session import ExpectSession


class TelnetSession(ExpectSession):
    SESSION_TYPE = 'TELNET'

    AUTHENTICATION_ERROR_PATTERN = '%.*($|\n)'

    def __init__(self, *args, **kwargs):
        ExpectSession.__init__(self, telnetlib.Telnet(), *args, **kwargs)

        if self._port is None:
            self._port = 23

    def __del__(self):
        self.disconnect()

    def connect(self, prompt, logger):
        """Open connection to device / create session

        :param prompt:
        :param logger:
        """

        self._handler.open(self._host, int(self._port), self._timeout)
        if self._handler.get_socket() is None:
            raise Exception('TelnetSession', "Failed to open telnet connection.")

        self._handler.get_socket().send(telnetlib.IAC + telnetlib.WILL + telnetlib.ECHO)

        action_map = OrderedDict()
        action_map['[Ll]ogin:|[Uu]ser:|[Uu]sername:'] = lambda session: session.send_line(session._username, logger)
        action_map['[Pp]assword:'] = lambda session: session.send_line(session._password, logger)
        out = self.hardware_expect(None, expected_string=prompt, timeout=self._timeout, logger=logger,
                                   action_map=action_map)
        self._default_actions(logger)

    def disconnect(self):
        """Disconnect / close the session

        :return:
        """

        self._handler.close()

    def _send(self, command, logger):
        """send message / command to device

        :param data_str: message / command to send
        :return:
        """

        self._handler.write(command)

    def _receive(self, timeout, logger):
        """read session buffer

        :param timeout:
        :return: output
        """

        timeout = timeout if timeout else self._timeout
        self._handler.get_socket().settimeout(timeout)

        data = self._handler.read_some()
        return data
