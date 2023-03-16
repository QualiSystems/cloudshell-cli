from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.service.auth_model import Auth
    from cloudshell.cli.service.console_model import ConsoleParams
    from cloudshell.cli.types import T_ON_SESSION_START, T_SESSION


class SessionFactory(ABC):
    """Session factory.

    Help to initialize session for specified session class.
    """

    def __init__(self, session_class, session_kwargs: dict[str, str] | None = None):
        """:param session_class: Session class."""
        self.session_class = session_class
        self.session_kwargs = session_kwargs or {}

    @property
    def session_type(self) -> str:
        return self.session_class.SESSION_TYPE

    @abstractmethod
    def init_session(
        self,
        host: str,
        port: int,
        auth: Auth,
        console_params: ConsoleParams | None,
        logger: Logger,
        on_session_start: T_ON_SESSION_START | None = None,
    ) -> T_SESSION:
        raise NotImplementedError


class GenericSessionFactory(SessionFactory):
    def init_session(
        self,
        host: str,
        port: int,
        auth: Auth,
        console_params: ConsoleParams | None,
        logger: Logger,
        on_session_start: T_ON_SESSION_START | None = None,
    ) -> T_SESSION:
        return self.session_class(
            host=host,
            port=port,
            username=auth.username,
            password=auth.password,
            on_session_start=on_session_start,
            **self.session_kwargs,
        )


class CloudInfoAccessKeySessionFactory(GenericSessionFactory):
    def init_session(
        self,
        host: str,
        port: int,
        auth: Auth,
        console_params: ConsoleParams | None,
        logger: Logger,
        on_session_start: T_ON_SESSION_START | None = None,
    ) -> T_SESSION:
        return self.session_class(
            host=host,
            port=port,
            username=auth.username,
            password=auth.password,
            pkey=auth.key,
            pkey_passphrase=auth.key_passphrase,
            on_session_start=on_session_start,
            **self.session_kwargs,
        )


class ConsoleSessionFactory(GenericSessionFactory):
    def __init__(
        self,
        session_class,
        console_auth: bool = False,
        session_kwargs: dict[str, Any] | None = None,
    ):
        super().__init__(session_class, session_kwargs)
        self.console_auth = console_auth

    @property
    def session_type(self) -> str:
        return "Console"

    def init_session(
        self,
        host: str,
        port: int,
        auth: Auth | None,
        console_params: ConsoleParams | None,
        logger: Logger,
        on_session_start: T_ON_SESSION_START | None = None,
    ) -> T_SESSION:
        assert console_params, "Console params are required for console session"
        username = console_params.username if self.console_auth else auth.username
        password = console_params.password if self.console_auth else auth.password
        host = console_params.host
        port = console_params.port
        return self.session_class(
            host=host,
            port=port,
            username=username,
            password=password,
            on_session_start=on_session_start,
            **self.session_kwargs,
        )
