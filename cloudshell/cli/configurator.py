#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import TYPE_CHECKING, Optional, Sequence

from cloudshell.cli.process.mode.command_mode import CommandMode
from cloudshell.cli.process.mode.manager import CommandModeContextManager
from cloudshell.cli.profiles.ssh.ssh_factory import SSHSessionFactory
from cloudshell.cli.profiles.ssh.ssh_session import SSHSession
from cloudshell.cli.session.manage.session_pool import SessionPoolManager

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})

if sys.version_info >= (3, 0):
    from functools import lru_cache
else:
    from functools32 import lru_cache

if TYPE_CHECKING:
    from cloudshell.cli.session.core.factory import AbstractSessionFactory
    from cloudshell.shell.core.driver_context import ReservationContextDetails
    from cloudshell.shell.standards.resource_config_generic_models import GenericCLIConfig


class FromResourceConfig(AbstractSessionFactory):
    @abstractmethod
    def init_from_resource_conf(self, resource_config: "GenericCLIConfig",
                                reservation_context: "ReservationContextDetails"):
        raise NotImplementedError


class CLIConfigurator(object):
    SESSION_FACTORIES = (SSHSessionFactory(SSHSession))
    """Using factories instead of """

    def __init__(
            self,
            resource_config: "GenericCLIConfig",
            reservation_context: Optional[ReservationContextDetails] = None,
            factories: Sequence["FromResourceConfig"] = None,
            session_pool: SessionPoolManager = None
    ):
        """Initialize CLI service configurator."""
        self._resource_config = resource_config
        self._reservation_context = reservation_context
        self._registered_factories: Sequence["FromResourceConfig"] = factories or self.SESSION_FACTORIES
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
        return factories_dict

    def initialize_params(self, factory: FromResourceConfig):
        factory.init_from_resource_conf(self._resource_config, self._reservation_context)

    def _get_factories(self) -> Sequence["AbstractSessionFactory"]:
        for factory in self._factories_dict.get(self._cli_type.upper(), sum(self._factories_dict.values(), [])):
            self.initialize_params(factory)
            yield factory

    def get_cli_service(self, command_mode: "CommandMode"):
        """Use cli.get_session to open CLI connection and switch into required mode."""

        return CommandModeContextManager(self._session_pool, self._get_factories(), command_mode)


class AbstractModeConfigurator(ABC, CLIConfigurator):
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
