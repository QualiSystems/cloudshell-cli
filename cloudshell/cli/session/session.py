from abc import ABCMeta, abstractmethod
from collections import OrderedDict

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})


class Session(ABC):
    @abstractmethod
    def connect(self, prompt, logger):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def _send(self, command, logger):
        pass

    @abstractmethod
    def send_line(self, command, logger):
        pass

    @abstractmethod
    def _receive(self, timeout, logger):
        pass

    @abstractmethod
    def hardware_expect(
        self,
        command,
        expected_string,
        logger,
        action_map=OrderedDict(),
        error_map=OrderedDict(),
        timeout=None,
        retries=None,
        check_action_loop_detector=True,
        empty_loop_timeout=None,
        **optional_args
    ):
        pass

    @abstractmethod
    def probe_for_prompt(self, expected_string, logger):
        pass

    @abstractmethod
    def match_prompt(self, prompt, match_string, logger):
        pass

    @abstractmethod
    def reconnect(self, prompt, logger, timeout=None):
        pass

    @abstractmethod
    def active(self):
        pass

    @abstractmethod
    def set_active(self, state):
        pass
