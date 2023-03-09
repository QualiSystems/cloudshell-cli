from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.types import T_ON_SESSION_START, T_SESSION


class SessionFactory(ABC):
    """Session factory.

    Help to initialize session for specified session class.
    """

    def __init__(self, session_class):
        """:param session_class: Session class."""
        self.session_class = session_class

    @abstractmethod
    def init_session(
        self,
        resource_config,
        logger: Logger,
        on_session_start: T_ON_SESSION_START | None = None,
        access_key: str | None = None,
        access_key_passphrase: str | None = None,
    ) -> T_SESSION:
        raise NotImplementedError


class GenericSessionFactory(SessionFactory):
    def init_session(
        self,
        resource_config,
        logger: Logger,
        on_session_start: T_ON_SESSION_START | None = None,
        access_key: str | None = None,
        access_key_passphrase: str | None = None,
    ) -> T_SESSION:
        return self.session_class(
            **self._session_kwargs(
                resource_config,
                logger,
                on_session_start,
                access_key,
                access_key_passphrase,
            )
        )

    @property
    def SESSION_TYPE(self) -> str:
        return self.session_class.SESSION_TYPE

    def _session_kwargs(
        self,
        resource_config,
        logger: Logger,
        on_session_start: T_ON_SESSION_START | None,
        access_key: str | None,
        access_key_passphrase: str | None,
    ) -> dict:
        return {
            "host": resource_config.address,
            "username": resource_config.user,
            "password": resource_config.password,
            "port": resource_config.cli_tcp_port,
            "on_session_start": on_session_start,
        }


class CloudInfoAccessKeySessionFactory(GenericSessionFactory):
    def _session_kwargs(
        self,
        resource_config,
        logger: Logger,
        on_session_start: T_ON_SESSION_START | None,
        access_key: str | None,
        access_key_passphrase: str | None,
    ):
        return {
            "host": resource_config.address,
            "username": resource_config.user,
            "password": resource_config.password,
            "port": resource_config.cli_tcp_port,
            "pkey": access_key,
            "pkey_passphrase": access_key_passphrase,
            "on_session_start": on_session_start,
        }
