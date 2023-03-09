from __future__ import annotations

import socket
from typing import TYPE_CHECKING

from cloudshell.cli.session.connection_params import ConnectionParams
from cloudshell.cli.session.expect_session import ExpectSession

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.types import T_ON_SESSION_START, T_TIMEOUT


class TCPSession(ExpectSession, ConnectionParams):
    SESSION_TYPE = "TCP"
    BUFFER_SIZE = 1024

    def __init__(
        self,
        host: str,
        port: int | None,
        on_session_start: T_ON_SESSION_START | None = None,
        *args,
        **kwargs,
    ):
        ConnectionParams.__init__(
            self, host=host, port=port, on_session_start=on_session_start
        )
        ExpectSession.__init__(self, *args, **kwargs)

        self._buffer_size = self.BUFFER_SIZE
        self._handler = None

    def _initialize_session(self, prompt: str, logger: Logger) -> None:
        self._handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (self.host, self.port)
        self._handler.connect(server_address)

        self._handler.settimeout(self._timeout)

    def probe_for_prompt(self, expected_string: str, logger: Logger) -> str:
        return "DUMMY_PROMPT"

    def _connect_actions(self, prompt: str, logger: Logger) -> None:
        self._on_session_start(logger)

    def disconnect(self) -> None:
        """Disconnect from device/close the session."""
        self._handler.close()
        self._active = False

    def _send(self, command: str, logger: Logger) -> None:
        """Send message to the session."""
        self._handler.sendall(command)

    def _set_timeout(self, timeout: T_TIMEOUT) -> None:
        self._handler.settimeout(timeout)

    def _read_byte_data(self) -> None:
        pass

    def _read_str_data(self) -> str:
        return self._handler.recv(self._buffer_size)
