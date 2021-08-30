from abc import ABCMeta, abstractmethod

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})


class AbstractSessionFactory(ABC):
    """Session Factory model.

    Create new session object.
    """

    def create_session(self, *args, **kwargs):
        raise NotImplementedError
