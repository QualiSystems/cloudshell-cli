from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.cli.service.cli_service_impl import CliServiceImpl as CliService
from cloudshell.cli.service.command_mode_helper import CommandModeHelper
from cloudshell.cli.session.expect_session import CommandExecutionException

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.service.command_mode import CommandMode
    from cloudshell.cli.service.session_pool import SessionPool
    from cloudshell.cli.types import T_SESSION


class SessionPoolContextManager:
    """Get and return session from pool and change mode if specified."""

    IGNORED_EXCEPTIONS = (CommandExecutionException,)

    def __init__(
        self,
        session_pool: SessionPool,
        defined_sessions: list[T_SESSION],
        command_mode: CommandMode,
        logger: Logger,
    ):
        self._session_pool = session_pool
        self._command_mode = command_mode
        self._logger = logger

        self._defined_sessions = defined_sessions

        self._active_session = None

    def _initialize_cli_service(self, session: T_SESSION, prompt: str) -> CliService:
        try:
            return CliService(session, self._command_mode, self._logger)
        except Exception:
            session.reconnect(prompt, self._logger)
            return CliService(session, self._command_mode, self._logger)

    def __enter__(self) -> CliService:
        prompts_re = r"|".join(
            CommandModeHelper.defined_modes_by_prompt(self._command_mode).keys()
        )
        self._active_session = self._session_pool.get_session(
            self._defined_sessions, prompts_re, self._logger
        )
        try:
            return self._initialize_cli_service(self._active_session, prompts_re)
        except Exception:
            self._session_pool.remove_session(self._active_session, self._logger)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._active_session:
            if (
                exc_type
                and not issubclass(exc_type, self.IGNORED_EXCEPTIONS)
                or not self._active_session.active()
            ):
                self._session_pool.remove_session(self._active_session, self._logger)
            else:
                self._session_pool.return_session(self._active_session, self._logger)
