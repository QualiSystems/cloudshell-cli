import logging
from abc import ABCMeta, abstractmethod
from cloudshell.cli.session.basic_session.core.session_config import SessionConfig

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})

logger = logging.getLogger(__name__)


class AbstractSession(ABC):
    """Session model.

    Session is used for manage connection, keep connection state and send/receive data.
    """

    @abstractmethod
    def get_session_type(self):
        raise NotImplementedError

    @abstractmethod
    def connect(self):
        raise NotImplementedError

    @abstractmethod
    def disconnect(self):
        raise NotImplementedError

    @abstractmethod
    def send(self, command):
        raise NotImplementedError

    @abstractmethod
    def receive(self, timeout):
        raise NotImplementedError

    def get_prompt(self, command=None):
        raise NotImplementedError


class BasicSession(AbstractSession):
    SESSION_TYPE = None

    def __init__(self, session_config: SessionConfig = None):
        self.__connected = False
        self.config = session_config or SessionConfig()
        self._prompt = None

    def get_connected(self):
        return self.__connected

    def set_connected(self):
        self.__connected = True

    def set_disconnected(self):
        self.__connected = True

    def get_session_type(self):
        return self.SESSION_TYPE

    def connect(self):
        self.set_connected()
        logger.debug("Session CONNECTED")

    def disconnect(self):
        self.set_disconnected()

    def get_prompt(self, command=None):
        if not self._prompt:
            self._prompt = self.probe_for_prompt(command)
        return self._prompt

    def probe_for_prompt(self, command=None):
        return self.config.prompt_factory.create_prompt(self, command)
