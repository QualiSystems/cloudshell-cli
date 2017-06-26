import socket
import telnetlib
from collections import OrderedDict

from cloudshell.cli.session.connection_params import ConnectionParams
from cloudshell.cli.session.expect_session import ExpectSession
from cloudshell.cli.session.session_exceptions import SessionException, SessionReadTimeout, SessionReadEmptyData


class TelnetSessionException(SessionException):
    pass


class TelnetSession(ExpectSession, ConnectionParams):
    SESSION_TYPE = 'TELNET'

    AUTHENTICATION_ERROR_PATTERN = '%.*($|\n)'

    def __init__(self, host, username, password, port=None, on_session_start=None, *args, **kwargs):
        ConnectionParams.__init__(self, host, port=port, on_session_start=on_session_start)
        ExpectSession.__init__(self, *args, **kwargs)

        if hasattr(self, 'port') and self.port is None:
            self.port = 23

        self.username = username
        self.password = password

        self._handler = None

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

    def _connect_actions(self, prompt, logger):
        action_map = OrderedDict()
        action_map['[Ll]ogin:|[Uu]ser:|[Uu]sername:'] = lambda session, logger: session.send_line(session.username,
                                                                                                  logger)
        action_map['[Pp]assword:'] = lambda session, logger: session.send_line(session.password, logger)
        self.hardware_expect(None, expected_string=prompt, timeout=self._timeout, logger=logger,
                                   action_map=action_map)
        self._on_session_start(logger)

    def _initialize_session(self, prompt, logger):
        self._handler = telnetlib.Telnet()

        self._handler.open(self.host, int(self.port), self._timeout)
        if self._handler.get_socket() is None:
            raise TelnetSessionException(self.__class__.__name__, "Failed to open telnet connection.")

        self._handler.get_socket().send(telnetlib.IAC + telnetlib.WILL + telnetlib.ECHO)

    def disconnect(self):
        """Disconnect / close the session

        :return:
        """
        if self._handler:
            self._handler.close()
        self._active = False

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

        try:
            data = self._handler.read_some()
        except socket.timeout:
            raise SessionReadTimeout()

        if not data:
            raise SessionReadEmptyData()

        return data
