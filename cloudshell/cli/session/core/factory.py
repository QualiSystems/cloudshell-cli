from abc import abstractmethod
from typing import TYPE_CHECKING, Type, Optional

if TYPE_CHECKING:
    from cloudshell.cli.session.core.session import Session
    from cloudshell.cli.session.core.config import SessionConfig


class AbstractSessionFactory(object):
    """Session Factory model.

    Create new session object.
    """

    def __init__(self, session_class: Type[Session], session_config: Optional[SessionConfig] = None):
        self.session_class = session_class
        self.config = session_config

    def get_session_type(self) -> str:
        return self.session_class.get_session_type()

    @abstractmethod
    def get_active_session(self) -> "Session":
        raise NotImplementedError

    def compatible(self, session: "Session") -> bool:
        return isinstance(session, self.session_class)
