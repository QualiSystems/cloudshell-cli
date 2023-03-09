from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.types import T_ON_SESSION_START


class ConnectionParams(ABC):
    """Session parameters."""

    def __init__(
        self,
        host: str,
        port: int | None = None,
        on_session_start: T_ON_SESSION_START | None = None,
        pkey: str | None = None,
    ):
        self.host = host
        self.port = None

        if port and int(port) != 0:
            self.port = int(port)

        if host:
            temp_host = host.split(":")
            self.host = temp_host[0]
            if not self.port and len(temp_host) > 1:
                self.port = int(temp_host[1])
        else:
            self.host = host

        self.on_session_start = on_session_start
        self.pkey = pkey

    def _on_session_start(self, logger: Logger) -> None:
        if self.on_session_start and callable(self.on_session_start):
            self.on_session_start(self, logger)

    def __eq__(self, other) -> bool:
        return (
            self.__class__ == other.__class__
            and self.host == other.host
            and self.port == other.port
            and self.pkey == other.pkey
        )
