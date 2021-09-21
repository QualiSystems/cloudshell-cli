from abc import ABCMeta, abstractmethod

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})


class CommandModeFactory(ABC):

    @abstractmethod
    def get_enable_mode(self):
        raise NotImplementedError

    @abstractmethod
    def get_config_mode(self):
        raise NotImplementedError
