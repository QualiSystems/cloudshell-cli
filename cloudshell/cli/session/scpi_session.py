from __future__ import annotations

import re
import socket
from typing import TYPE_CHECKING

from cloudshell.cli.session.tcp_session import TCPSession

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.types import (
        T_ACTION_MAP,
        T_ERROR_MAP,
        T_ON_SESSION_START,
        T_TIMEOUT,
    )


class SCPISession(TCPSession):
    SESSION_TYPE = "SCPI"
    BUFFER_SIZE = 1024

    def __init__(
        self,
        host: str,
        port: int | None,
        on_session_start: T_ON_SESSION_START | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(host, port, on_session_start, *args, **kwargs)

    def _initialize_session(self, prompt: str, logger: Logger) -> None:
        self._handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (self.host, self.port)
        self._handler.connect(server_address)
        self._handler.settimeout(self._timeout)

    def _connect_actions(self, prompt: str, logger: Logger) -> None:
        self._on_session_start(logger)

    def probe_for_prompt(self, expected_string: str, logger: Logger) -> str:
        return "DUMMY_PROMPT"

    def hardware_expect(
        self,
        command: str | None,
        expected_string: str,
        logger: Logger,
        action_map: T_ACTION_MAP | None = None,
        error_map: T_ERROR_MAP | None = None,
        timeout: T_TIMEOUT | None = None,
        retries: int | None = None,
        check_action_loop_detector: bool = True,
        empty_loop_timeout: T_TIMEOUT | None = None,
        remove_command_from_output: bool = True,
        **optional_args,
    ) -> str:
        if ";:system:error?" not in command.lower():
            command += ";:system:error?"

        statusre = r'([-0-9]+), "(.*)"[\r\n]*$'

        # avoid 'multiple repeat' error from '?' in the command - bug in expect_session
        remove_command_from_output = False

        rv = super().hardware_expect(
            command,
            statusre,
            logger,
            action_map,
            error_map,
            timeout,
            retries,
            check_action_loop_detector,
            empty_loop_timeout,
            remove_command_from_output,
            **optional_args,
        )

        m = re.search(statusre, rv)
        if not m:
            raise Exception("SCPI status code not found in output: %s" % rv)

        code, message = m.groups()
        if code < 0:
            raise Exception("SCPI error: %d: %s" % (code, message))

        return rv
