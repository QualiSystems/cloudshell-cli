import logging
import time
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Optional

from cloudshell.cli.session.basic_session.core.session_config import SessionConfig
from cloudshell.cli.session.basic_session.helper.send_receive import check_active

if TYPE_CHECKING:
    from cloudshell.cli.session.basic_session.prompt.prompt import AbstractPrompt

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})

logger = logging.getLogger(__name__)


class AbstractSession(ABC):
    """Session model.

    Session is used for manage connection, keep connection state and send/receive data.
    """
    SESSION_TYPE = None

    def __init__(self, session_config: SessionConfig = None):
        self.__connected = False
        self._last_activity = None
        self.config = session_config or SessionConfig()
        self._prompt = None

    def get_connected(self) -> bool:
        return self.__connected

    def get_session_type(self) -> str:
        return self.SESSION_TYPE

    @abstractmethod
    def send(self, command: str) -> None:
        pass

    def receive(self, timeout=Optional[int]) -> str:
        self.set_active()

    def connect(self) -> None:
        self.__connected = True
        logger.debug("Session is CONNECTED")

    def disconnect(self) -> None:
        self.__connected = False
        logger.debug("Session is DISCONNECTED")

    def get_prompt(self, command: str = None) -> "AbstractPrompt":
        if not self._prompt:
            self._prompt = self.probe_for_prompt(command)
        return self._prompt

    def probe_for_prompt(self, command: str = None) -> AbstractPrompt:
        return self.config.prompt_factory.create_prompt(self, command)

    def discard_current_prompt(self) -> None:
        self._prompt = None

    def set_active(self) -> None:
        self._last_activity = time.time()

    def check_active(self) -> bool:
        logger.debug("Check active")
        return check_active(self)

    def get_active(self) -> bool:
        if not self.get_connected():
            return False

        if self._last_activity and (time.time() -
                                    self._last_activity < self.config.active_timeout):
            return True
        else:
            return self.check_active()
