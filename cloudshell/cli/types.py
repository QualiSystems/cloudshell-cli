from __future__ import annotations

from logging import Logger
from typing import Callable, Union

from typing_extensions import TypeAlias

from cloudshell.cli.service.cli_service_impl import EnterCommandModeContextManager
from cloudshell.cli.service.command_mode import CommandMode
from cloudshell.cli.session.expect_session import ExpectSession
from cloudshell.cli.session.session_exceptions import CommandExecutionException

T_TIMEOUT = Union[float, int]

T_SESSION: TypeAlias = ExpectSession

T_ON_SESSION_START = Callable[[T_SESSION, Logger], None]

T_ACTION_MAP = dict[str, Callable[[T_SESSION, Logger], None]]
T_ERROR_MAP = dict[str, Union[CommandExecutionException, str]]

T_COMMAND_MODE_CONTEXT_MANAGER: TypeAlias = EnterCommandModeContextManager

T_COMMAND_MODE_RELATIONS: TypeAlias = dict[type[CommandMode] : dict]
