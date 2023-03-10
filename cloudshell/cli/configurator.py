from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from functools import lru_cache
from typing import TYPE_CHECKING, ClassVar

from attrs import define, field

from cloudshell.cli.factory.session_factory import (
    CloudInfoAccessKeySessionFactory,
    GenericSessionFactory,
    SessionFactory,
)
from cloudshell.cli.service.auth_model import Auth
from cloudshell.cli.service.cli import CLI
from cloudshell.cli.service.console_model import ConsoleParams
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession

if TYPE_CHECKING:
    from collections.abc import Collection
    from logging import Logger

    from cloudshell.cli.service.command_mode import CommandMode
    from cloudshell.cli.service.session_pool_context_manager import (
        SessionPoolContextManager,
    )
    from cloudshell.cli.types import T_SESSION, CliConfigProtocol


@define
class CLIServiceConfigurator:
    REGISTERED_SESSIONS: ClassVar[tuple[SessionFactory]] = (
        CloudInfoAccessKeySessionFactory(SSHSession),
        GenericSessionFactory(TelnetSession),
    )

    _cli_type: str
    _host: str
    _logger: Logger
    _port: int = 0
    _auth: Auth = field(factory=Auth)
    _console_params: ConsoleParams | None = None
    _cli: CLI = field(factory=CLI)
    _registered_sessions: Collection[SessionFactory] = REGISTERED_SESSIONS

    @classmethod
    def from_config(
        cls,
        conf: CliConfigProtocol,
        logger: Logger,
        cli: CLI | None = None,
        registered_sessions: Collection[SessionFactory] | None = REGISTERED_SESSIONS,
    ) -> CLIServiceConfigurator:
        if not cli:
            cli = CLI()
        auth = Auth(
            conf.user,
            conf.password,
            conf.enable_password,
            conf.access_key,
            conf.access_key_passphrase,
        )
        console_params = ConsoleParams(
            conf.console_server_ip_address,
            conf.console_user,
            conf.console_password,
            conf.console_port,
        )
        return cls(
            conf.cli_connection_type.value,
            conf.address,
            logger,
            port=conf.cli_tcp_port,
            auth=auth,
            console_params=console_params,
            cli=cli,
            registered_sessions=registered_sessions,
        )

    @property
    @lru_cache()
    def _session_dict(self) -> defaultdict[str, list[SessionFactory]]:
        session_dict = defaultdict(list)
        for sess in self._registered_sessions:
            session_dict[sess.session_type.lower()].append(sess)
        return session_dict

    def _on_session_start(self, session: T_SESSION, logger: Logger) -> None:
        pass

    def initialize_session(self, session: SessionFactory) -> T_SESSION:
        return session.init_session(
            host=self._host,
            port=self._port,
            auth=self._auth,
            console_params=self._console_params,
            logger=self._logger,
            on_session_start=self._on_session_start,
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
