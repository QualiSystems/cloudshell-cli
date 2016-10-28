import telnetlib
from collections import OrderedDict

from cloudshell.cli.session.connection_params import ConnectionParams

from cloudshell.cli.session.expect_session import ExpectSession


class TelnetSession(ExpectSession, ConnectionParams):
    SESSION_TYPE = 'TELNET'

    AUTHENTICATION_ERROR_PATTERN = '%.*($|\n)'

    def __init__(self, host, username, password, port=None, on_session_start=None):
        ConnectionParams.__init__(self, host, port=port, on_session_start=on_session_start)

        if self.port is None:
            self.port = 23

        self.username = username
        self.password = password

        self._handler = None
        self._active = False

    def __eq__(self, other):
        """
        :param other:
        :type other: TelnetSession
        :return:
        """
        return ConnectionParams.__eq__(self,
                                       other) and self.username == other.username and self.password == other.password

    def __del__(self):
        self.disconnect()

    def connect(self, prompt, logger):
        """Open connection to device / create session

        :param prompt:
        :param logger:
        """
        ExpectSession.__init__(self)
        self._handler = telnetlib.Telnet()

        self._handler.open(self.host, int(self.port), self._timeout)
        if self._handler.get_socket() is None:
            raise Exception('TelnetSession', "Failed to open telnet connection.")

        self._handler.get_socket().send(telnetlib.IAC + telnetlib.WILL + telnetlib.ECHO)

        action_map = OrderedDict()
        action_map['[Ll]ogin:|[Uu]ser:|[Uu]sername:'] = lambda session, logger: session.send_line(session.username,
                                                                                                  logger)
        action_map['[Pp]assword:'] = lambda session, logger: session.send_line(session.password, logger)
        out = self.hardware_expect(None, expected_string=prompt, timeout=self._timeout, logger=logger,
                                   action_map=action_map)
        if self.on_session_start and callable(self.on_session_start):
            self.on_session_start(self, logger)
        self._active = True

    def disconnect(self):
        """Disconnect / close the session

        :return:
        """
        if self._handler:
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
