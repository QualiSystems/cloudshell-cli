from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from cloudshell.cli.service.session_pool_context_manager import (
    SessionPoolContextManager,
)
from cloudshell.cli.service.session_pool_manager import SessionPoolManager

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.service.command_mode import CommandMode
    from cloudshell.cli.types import T_SESSION


class CLI:
    def __init__(self, session_pool: SessionPoolManager = SessionPoolManager()):
        self._session_pool = session_pool

    def get_session(
        self,
        defined_sessions: list[T_SESSION],
        command_mode: CommandMode,
        logger: Logger | None = None,
    ) -> SessionPoolContextManager:
        """Get session from the pool or create new."""
        if not isinstance(defined_sessions, list):
            defined_sessions = [defined_sessions]

        if not logger:
            logger = logging.getLogger("cloudshell_cli")
        return SessionPoolContextManager(
            self._session_pool, defined_sessions, command_mode, logger
        )
