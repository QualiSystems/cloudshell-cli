from __future__ import annotations

from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.cli.types import T_ACTION_MAP, T_ON_SESSION_START


class ConsoleTelnetSession(TelnetSession):
    SESSION_TYPE = "CONSOLE_TELNET"

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int | None = None,
        on_session_start: T_ON_SESSION_START | None = None,
        start_with_new_line: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(
            host,
            username,
            password,
            port,
            on_session_start,
            loop_detector_max_action_loops=5,
            *args,
            **kwargs,
        )
        self._start_with_new_line = start_with_new_line

    @property
    def _connect_command(self) -> str | None:
        cmd = "" if self._start_with_new_line else None
        return cmd

    @property
    def _connect_action_map(self) -> T_ACTION_MAP:
        def empty_action(ses, log):
            ses.send_line("", log)
            if empty_key in action_map:
                del action_map[empty_key]

        empty_key = r".*"
        action_map = super()._connect_action_map
        action_map[empty_key] = empty_action
        return action_map
