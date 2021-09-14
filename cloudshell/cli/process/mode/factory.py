from abc import ABCMeta, abstractmethod

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})


class CommandModeFactory(ABC):

    @abstractmethod
    def enable_mode(self):
        raise NotImplementedError

    @abstractmethod
    def config_mode(self):
        raise NotImplementedError
