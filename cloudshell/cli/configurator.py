from abc import ABC, abstractmethod
from collections import defaultdict
from functools import lru_cache

from cloudshell.cli.factory.session_factory import (
    CloudInfoAccessKeySessionFactory,
    GenericSessionFactory,
    SessionFactory,
)
from cloudshell.cli.service.cli import CLI
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession


class CLIServiceConfigurator:
    REGISTERED_SESSIONS = (CloudInfoAccessKeySessionFactory(SSHSession), TelnetSession)

    def __init__(
        self,
        resource_config,
        logger,
        cli=None,
        registered_sessions=None,
        access_key=None,
        access_key_passphrase=None,
    ):
        """Initialize CLI service configurator.

        :param cloudshell.shell.standards.resource_config_generic_models.GenericCLIConfig resource_config:  # noqa: E501
        :param logging.Logger logger:
        :param cloudshell.cli.service.cli.CLI cli:
        :param registered_sessions: Session types and order
        :param access_key: access key for the resource
        :param access_key_passphrase: access key passphrase for the resource
        """
        self._cli = cli or CLI()
        self._resource_config = resource_config
        self._logger = logger
        self._registered_sessions = registered_sessions or self.REGISTERED_SESSIONS
        self._access_key = access_key
        self._access_key_passphrase = access_key_passphrase

    @property
    def _cli_type(self):
        """Connection type property [ssh|telnet|console|auto]."""
        return self._resource_config.cli_connection_type

    @property
    @lru_cache()
    def _session_dict(self):
        session_dict = defaultdict(list)
        for sess in self._registered_sessions:
            session_dict[sess.SESSION_TYPE.lower()].append(sess)
        return session_dict

    def _on_session_start(self, session, logger):
        pass

    def initialize_session(self, session):
        if not isinstance(session, SessionFactory):
            session = GenericSessionFactory(session)
        return session.init_session(
            self._resource_config,
            self._logger,
            on_session_start=self._on_session_start,
            access_key=self._access_key,
            access_key_passphrase=self._access_key_passphrase,
        )

    def _defined_sessions(self):
        return [
            self.initialize_session(sess)
            for sess in self._session_dict.get(
                self._cli_type.lower(), self._registered_sessions
            )
        ]

    def get_cli_service(self, command_mode):
        """Use cli.get_session to open CLI connection and switch into required mode.

        :param CommandMode command_mode: operation mode, can be
            default_mode/enable_mode/config_mode/etc.
        :return: created session in provided mode
        :rtype: cloudshell.cli.service.session_pool_context_manager.SessionPoolContextManager  # noqa: E501
        """
        return self._cli.get_session(
            self._defined_sessions(), command_mode, self._logger
        )


class AbstractModeConfigurator(ABC, CLIServiceConfigurator):
    """Used by shells to run enable/config command."""

    @property
    @abstractmethod
    def enable_mode(self):
        pass

    @property
    @abstractmethod
    def config_mode(self):
        pass

    def enable_mode_service(self):
        return self.get_cli_service(self.enable_mode)

    def config_mode_service(self):
        return self.get_cli_service(self.config_mode)
