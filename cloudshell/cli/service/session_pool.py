from abc import ABCMeta, abstractmethod

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})


class SessionPool(ABC):
    @abstractmethod
    def get_session(self, new_sessions, prompt, logger):
        """Get session from pool.

        :rtype: cloudshell.cli.session.session.Session
        """
        pass

    @abstractmethod
    def return_session(self, session, logger):
        """Return session to pool.

        :type session: cloudshell.cli.session.session.Session
        :type logger: logging.Logger
        """
        pass

    @abstractmethod
    def remove_session(self, session, logger):
        """Remove session from pool.

        :type session: cloudshell.cli.session.session.Session
        :type logger: logging.Logger
        """
        pass
