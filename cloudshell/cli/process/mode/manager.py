from typing import TYPE_CHECKING, List, Optional

from cloudshell.cli.process.command.exception import CommandExecutionException
from cloudshell.cli.process.command.processor import CommandProcessor
from cloudshell.cli.process.mode.command_mode import CommandMode
from cloudshell.cli.process.mode.command_mode_helper import CommandModeHelper
from cloudshell.cli.session.core.factory import AbstractSessionFactory
from cloudshell.cli.session.core.session import Session

if TYPE_CHECKING:
    from cloudshell.cli.session.manage.session_pool import SessionPoolManager


class CommandModeContextManager(object):
    """Get and return session from pool and change mode if specified."""

    IGNORED_EXCEPTIONS = (CommandExecutionException,)

    def __init__(self, session_pool: "SessionPoolManager", session_factories: List["AbstractSessionFactory"],
                 command_mode: "CommandMode"):
        """Initialize Session pool context manager."""
        self._session_pool = session_pool
        self._command_mode = command_mode

        self._session_factories = session_factories

        self._active_session: Optional["Session"] = None

    def __enter__(self) -> CommandProcessor:
        """Enter."""

        self._active_session = self._session_pool.get_session(self._session_factories)
        command_processor = CommandProcessor(self._active_session)
        current_mode = CommandModeHelper.determine_current_mode(command_processor, self._command_mode)
        CommandModeHelper.change_mode(command_processor, current_mode, self._command_mode)
        return command_processor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._active_session is not None:
            if (exc_type
                    and not issubclass(exc_type, self.IGNORED_EXCEPTIONS)
                    or not self._active_session.get_active()
            ):
                self._session_pool.remove_session(self._active_session)
            else:
                self._session_pool.return_session(self._active_session)
