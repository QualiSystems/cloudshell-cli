from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from functools import lru_cache
from typing import TYPE_CHECKING

from cloudshell.cli.factory.session_factory import (
    CloudInfoAccessKeySessionFactory,
    GenericSessionFactory,
    SessionFactory,
)
from cloudshell.cli.service.cli import CLI
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession

if TYPE_CHECKING:
    from collections.abc import Collection
    from logging import Logger

    from cloudshell.cli.service.command_mode import CommandMode
    from cloudshell.cli.service.session_pool_context_manager import (
        SessionPoolContextManager,
    )
    from cloudshell.cli.types import T_SESSION


class CLIServiceConfigurator:
    REGISTERED_SESSIONS: tuple[SessionFactory] = (
        CloudInfoAccessKeySessionFactory(SSHSession),
        GenericSessionFactory(TelnetSession),
    )

    def __init__(
        self,
        resource_config,
        logger: Logger,
        cli: CLI | None = None,
        registered_sessions: Collection[SessionFactory] | None = None,
        access_key: str | None = None,
        access_key_passphrase: str | None = None,
    ):
        self._cli = cli or CLI()
        self._resource_config = resource_config
        self._logger = logger
        self._registered_sessions = registered_sessions or self.REGISTERED_SESSIONS
        self._access_key = access_key
        self._access_key_passphrase = access_key_passphrase

    @property
    def _cli_type(self) -> str:
        """Connection type property [ssh|telnet|console|auto]."""
        return self._resource_config.cli_connection_type.value

    @property
    @lru_cache()
    def _session_dict(self) -> defaultdict[str, list[SessionFactory]]:
        session_dict = defaultdict(list)
        for sess in self._registered_sessions:
            session_dict[sess.SESSION_TYPE.lower()].append(sess)
        return session_dict

    def _on_session_start(self, session: T_SESSION, logger: Logger) -> None:
        pass

    def initialize_session(self, session: SessionFactory) -> T_SESSION:
        return session.init_session(
            self._resource_config,
            self._logger,
            on_session_start=self._on_session_start,
            access_key=self._access_key,
            access_key_passphrase=self._access_key_passphrase,
        )

    def _defined_sessions(self) -> list[T_SESSION]:
        return [
            self.initialize_session(sess)
            for sess in self._session_dict.get(
                self._cli_type.lower(), self._registered_sessions
            )
        ]

    def get_cli_service(self, command_mode: CommandMode) -> SessionPoolContextManager:
        """Use cli.get_session to open CLI connection and switch into required mode.

        :param command_mode: operation mode, can be
            default_mode/enable_mode/config_mode/etc.
        :return: created session in provided mode
        """
        return self._cli.get_session(
            self._defined_sessions(), command_mode, self._logger
        )


class AbstractModeConfigurator(ABC, CLIServiceConfigurator):
    """Used by shells to run enable/config command."""

    @property
    @abstractmethod
    def enable_mode(self) -> CommandMode:
        pass

    @property
    @abstractmethod
    def config_mode(self) -> CommandMode:
        pass

    def enable_mode_service(self) -> SessionPoolContextManager:
        return self.get_cli_service(self.enable_mode)

    def config_mode_service(self) -> SessionPoolContextManager:
        return self.get_cli_service(self.config_mode)
