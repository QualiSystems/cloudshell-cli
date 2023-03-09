from __future__ import annotations

import re
import socket
from typing import TYPE_CHECKING

from cloudshell.cli.session.connection_params import ConnectionParams
from cloudshell.cli.session.tcp_session import TCPSession

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.types import (
        T_ACTION_MAP,
        T_ERROR_MAP,
        T_ON_SESSION_START,
        T_TIMEOUT,
    )


class TL1Session(TCPSession):
    SESSION_TYPE = "TL1"
    BUFFER_SIZE = 1024

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int | None,
        on_session_start: T_ON_SESSION_START | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(host, port, on_session_start, *args, **kwargs)
        self._username = username
        self._password = password
        self.switch_name = "switch-name-not-initialized"
        self._tl1_counter = 0

    def __eq__(self, other) -> bool:
        return (
            ConnectionParams.__eq__(self, other)
            and self._username == other._username
            and self._password == other._password
        )

    def probe_for_prompt(self, expected_string: str, logger: Logger) -> str:
        return "DUMMY_PROMPT"

    def _initialize_session(self, prompt: str, logger: Logger) -> None:
        self._handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (self.host, self.port)
        self._handler.connect(server_address)
        self._handler.settimeout(self._timeout)

    def _connect_actions(self, prompt: str, logger: Logger) -> None:
        output = self.hardware_expect(
            f"ACT-USER::{self._username}:{{counter}}::{self._password};",
            expected_string=None,
            logger=logger,
        )
        if "( nil )" in output:
            self.switch_name = ""
            logger.info('Switch name was "( nil )" - using blank switch name')
        else:
            m = re.search(r"(\S+)", output)
            if m:
                self.switch_name = m.groups()[0]
                logger.info('Taking as switch name: "%s"' % self.switch_name)
            else:
                logger.warn(
                    "Switch name regex not found: %s - using blank switch name" % output
                )
                self.switch_name = ""
        if self.on_session_start and callable(self.on_session_start):
            self.on_session_start(self, logger)
        self._active = True

    def hardware_expect(
        self,
        command: str | None,
        expected_string: str | None,
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
        self._tl1_counter += 1
        command = command.replace("{counter}", str(self._tl1_counter))
        command = command.replace("{name}", self.switch_name)
        prompt = r"M\s+%d\s+([A-Z ]+)[^;]*;" % self._tl1_counter

        rv = super().hardware_expect(
            command,
            prompt,
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

        m = re.search(prompt, rv)
        status = m.groups()[0]
        if status != "COMPLD":
            raise Exception(f'Error: Status "{status}": {rv}')
        return rv
