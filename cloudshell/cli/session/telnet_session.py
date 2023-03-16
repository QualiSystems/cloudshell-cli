from __future__ import annotations

import telnetlib
from typing import TYPE_CHECKING

from cloudshell.cli.session.connection_params import ConnectionParams
from cloudshell.cli.session.expect_session import ExpectSession
from cloudshell.cli.session.session_exceptions import SessionException

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.types import T_ACTION_MAP, T_ON_SESSION_START, T_TIMEOUT


class TelnetSessionException(SessionException):
    pass


class TelnetSession(ExpectSession, ConnectionParams):
    SESSION_TYPE = "TELNET"

    AUTHENTICATION_ERROR_PATTERN = "%.*($|\n)"

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int | None = None,
        on_session_start: T_ON_SESSION_START | None = None,
        *args,
        **kwargs,
    ):
        ConnectionParams.__init__(
            self, host, port=port, on_session_start=on_session_start
        )
        ExpectSession.__init__(self, *args, **kwargs)

        if hasattr(self, "port") and self.port is None:
            self.port = 23

        self.username = username
        self.password = password

        self._handler = None

    def __eq__(self, other) -> bool:
        return (
            ConnectionParams.__eq__(self, other)
            and self.username == other.username
            and self.password == other.password
        )

    def __del__(self) -> None:
        self.disconnect()

    @property
    def _connect_action_map(self) -> T_ACTION_MAP:
        action_map = {
            "[Ll]ogin:|[Uu]ser:|[Uu]sername:": lambda s, l: s.send_line(s.username, l),
            "[Pp]assword:": lambda s, l: s.send_line(s.password, l),
        }
        return action_map

    @property
    def _connect_command(self) -> str | None:
        return None

    def _connect_actions(self, prompt: str, logger: Logger) -> None:
        self.hardware_expect(
            self._connect_command,
            expected_string=prompt,
            timeout=self._timeout,
            logger=logger,
            action_map=self._connect_action_map,
        )
        self._on_session_start(logger)

    def _initialize_session(self, prompt: str, logger: Logger) -> None:
        self._handler = telnetlib.Telnet()

        self._handler.open(self.host, int(self.port), self._timeout)
        if self._handler.get_socket() is None:
            raise TelnetSessionException(
                self.__class__.__name__, "Failed to open telnet connection."
            )

        self._handler.get_socket().send(telnetlib.IAC + telnetlib.WILL + telnetlib.ECHO)

    def disconnect(self) -> None:
        """Disconnect / close the session."""
        if self._handler:
            self._handler.close()
        self._active = False

    def _send(self, command: str, logger: Logger) -> None:
        """Send message / command to device."""
        byte_command = command.encode()
        self._handler.write(byte_command)

    def _set_timeout(self, timeout: T_TIMEOUT) -> None:
        self._handler.get_socket().settimeout(timeout)

    def _read_byte_data(self) -> bytes:
        return self._handler.read_some()
