from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.cli.session.ssh_session import SSHSession

if TYPE_CHECKING:
    from logging import Logger


class ConsoleSSHSession(SSHSession):
    SESSION_TYPE = "CONSOLE_SSH"

    def connect(self, prompt: str, logger: Logger) -> None:
        try:
            super().connect(prompt, logger)
        except Exception:
            self.disconnect()
            raise
