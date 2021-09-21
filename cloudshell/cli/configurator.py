#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from functools import lru_cache
from typing import TYPE_CHECKING, Optional, Sequence

from cloudshell.cli.process.mode.command_mode import CommandMode
from cloudshell.cli.process.mode.manager import CommandModeContextManager
from cloudshell.cli.profiles.ssh.ssh_factory import SSHFromResourceConfig
from cloudshell.cli.profiles.ssh.ssh_session import SSHSession
from cloudshell.cli.session.manage.session_pool import SessionPoolManager

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})

if TYPE_CHECKING:
    from cloudshell.cli.session.core.factory import SessionFactory, FromResourceConfigFactory
    from cloudshell.shell.core.driver_context import ReservationContextDetails
    from cloudshell.shell.standards.resource_config_generic_models import GenericCLIConfig

logger = logging.getLogger(__name__)


class CLIConfigurator(object):
    SESSION_FACTORIES = (SSHFromResourceConfig(SSHSession))
    """Using factories instead of """

    def __init__(
            self,
            resource_config: "GenericCLIConfig",
            reservation_context: Optional["ReservationContextDetails"] = None,
            factories: Optional[Sequence["FromResourceConfigFactory"]] = None,
            session_pool: Optional[SessionPoolManager] = None
    ):
        """Initialize CLI service configurator."""
        self._resource_config = resource_config
        self._reservation_context = reservation_context
        self._registered_factories: Sequence["FromResourceConfigFactory"] = factories or self.SESSION_FACTORIES
        self._session_pool = session_pool

    @property
    def _cli_type(self) -> str:
        """Connection type property [ssh|telnet|console|auto]."""
        return self._resource_config.cli_connection_type

    @property
    @lru_cache()
    def _factories_dict(self):
        factories_dict = defaultdict(list)
        for factory in self._registered_factories:
            factories_dict[factory.get_session_type().upper()].append(factory)

        logger.debug(f"Available {','.format(factories_dict.keys())}")
        return factories_dict

    def initialize_params(self, factory: "FromResourceConfigFactory"):
        factory.init_from_resource_conf(self._resource_config, self._reservation_context)

    def _get_factories(self) -> Sequence["SessionFactory"]:
        for factory in self._factories_dict.get(self._cli_type.upper(), sum(self._factories_dict.values(), [])):
            self.initialize_params(factory)
            yield factory

    def get_cli_service(self, command_mode: "CommandMode") -> CommandModeContextManager:
        """Use cli.get_session to open CLI connection and switch into required mode."""

        return CommandModeContextManager(self._session_pool, self._get_factories(), command_mode)


class AbstractModeConfigurator(CLIConfigurator):
    """Used by shells to run enable/config command."""

    @abstractmethod
    def _get_enable_mode(self):
        raise NotImplementedError

    @abstractmethod
    def _get_config_mode(self):
        raise NotImplementedError

    def enable_mode_service(self) -> CommandModeContextManager:
        return self.get_cli_service(self._get_enable_mode())

    def config_mode_service(self) -> CommandModeContextManager:
        return self.get_cli_service(self._get_config_mode())
