from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cloudshell.cli.session.core.session import Session

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})


class AbstractSessionFactory(ABC):
    """Session Factory model.

    Create new session object.
    """

    @abstractmethod
    def get_type(self):
        raise NotImplementedError

    @abstractmethod
    def get_session(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def compatible(self, session: "Session"):
        raise NotImplementedError
