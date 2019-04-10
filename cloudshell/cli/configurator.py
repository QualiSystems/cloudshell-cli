#!/usr/bin/python
# -*- coding: utf-8 -*-
import functools
from abc import ABC, abstractmethod

from cloudshell.cli.service.cli import CLI
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession


class CLIServiceConfigurator(object):
    REGISTERED_SESSIONS = (SSHSession, TelnetSession)

    def __init__(self, resource_config, logger, api, cli=None, registered_sessions=REGISTERED_SESSIONS):
        """
        :param cloudshell.shell_standards.resource_config_generic_models.GenericCLIConfig resource_config:
        :param logging.Logger logger:
        :param cloudshell.api.cloudshell_api.CloudShellAPISession api:
        :param cloudshell.cli.service.cli.CLI cli:
        :param registered_sessions: Session types and order
        """
        self._cli = cli or CLI()
        self._resource_config = resource_config
        self._logger = logger
        self._api = api
        self._registered_sessions = registered_sessions

    @property
    def _username(self):
        return self._resource_config.user

    @property
    @functools.lru_cache()
    def _password(self):
        return self._api.DecryptPassword(self._resource_config.password).Value

    @property
    def _resource_address(self):
        """Resource IP

        :return:
        """
        return self._resource_config.address

    @property
    def _port(self):
        """Connection port property, to open socket on

        :return:
        """
        return self._resource_config.cli_tcp_port

    @property
    def _cli_type(self):
        """Connection type property [ssh|telnet|console|auto]

        :return:
        """
        return self._resource_config.cli_connection_type

    @property
    @functools.lru_cache()
    def _session_dict(self):
        return {sess.SESSION_TYPE.lower(): [sess] for sess in self._registered_sessions}

    def _on_session_start(self, session, logger):
        """Perform some default commands when session just opened (like 'no logging console')

        :param session:
        :param logger:
        :return:
        """
        pass

    @property
    @functools.lru_cache()
    def _session_kwargs(self):
        return {'host': self._resource_address,
                'username': self._username,
                'password': self._password,
                'port': self._port,
                'on_session_start': self._on_session_start}

    def _defined_sessions(self):
        return map(lambda sess: sess(**self._session_kwargs),
                   self._session_dict.get(self._cli_type.lower(), self._registered_sessions))

    def get_cli_service(self, command_mode):
        """Use cli.get_session to open CLI connection and switch into required mode

        :param CommandMode command_mode: operation mode, can be default_mode/enable_mode/config_mode/etc.
        :return: created session in provided mode
        :rtype: cloudshell.cli.service.session_pool_context_manager.SessionPoolContextManager
        """
        return self._cli.get_session(self._defined_sessions(), command_mode, self._logger)


class EnableConfigModeConfigurator(ABC, CLIServiceConfigurator):
    """
    Used by shells to run enable/config command
    """

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
