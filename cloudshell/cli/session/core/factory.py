import logging
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Type, Optional, Callable

from cloudshell.cli.session.core.exception import SessionFactoryException

if TYPE_CHECKING:
    from cloudshell.cli.session.core.session import Session
    from cloudshell.cli.session.core.config import SessionConfig
    from cloudshell.cli.session.core.connection_params import ConnectionParams
    from cloudshell.shell.standards.resource_config_generic_models import GenericCLIConfig
    from cloudshell.shell.core.driver_context import ReservationContextDetails
    from cloudshell.shell.standards.resource_config_generic_models import GenericCLIConfig

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})

logger = logging.getLogger(__name__)


class SessionFactory(object):
    """Session Factory model.

    Create new session object.
    """

    def __init__(self, session_class: Type["Session"],
                 session_config: Optional["SessionConfig"] = None,
                 params: Optional["ConnectionParams"] = None,
                 connect_actions: Callable[["Session"], None] = None):
        self._session_class = session_class
        self._config = session_config
        self._params = params
        self._connect_actions = connect_actions

    def get_params(self) -> "ConnectionParams":
        if self._params is None:
            raise SessionFactoryException("Cannot call undefined params.")
        return self._params

    def set_params(self, params: "ConnectionParams") -> None:
        self._params = params

    def get_session_type(self) -> str:
        return self._session_class.get_session_type()

    def get_active_session(self) -> "Session":
        logger.debug(f"Creating new {self.get_session_type()} session")
        session = self._session_class(params=self.get_params(), session_config=self._config)
        self._do_connect_actions(session)
        return session

    def _do_connect_actions(self, session: "Session") -> None:
        logger.debug("Connect actions")
        session.connect()
        if not session.get_active():
            raise SessionFactoryException("Session is not active")
        if self._connect_actions:
            self._connect_actions(session)

    def compatible(self, session: "Session") -> bool:
        return (isinstance(session, self._session_class)
                and self.get_params() == session.params)


class FromResourceConfigFactory(SessionFactory):
    @abstractmethod
    def init_from_resource_conf(self, resource_config: "GenericCLIConfig",
                                reservation_context: "ReservationContextDetails"):
        raise NotImplementedError
