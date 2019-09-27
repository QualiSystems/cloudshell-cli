from abc import ABCMeta, abstractmethod

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})


class SessionManager(ABC):
    @abstractmethod
    def new_session(self, new_sessions, prompt, logger):
        """Create new session with specific session type defined in sessions_params."""
        pass

    @abstractmethod
    def existing_sessions_count(self):
        """Count of existing sessions.

        :rtype: int
        """
        pass

    @abstractmethod
    def remove_session(self, session, logger):
        """Remove session."""
        pass

    @abstractmethod
    def is_compatible(self, session, new_sessions, logger):
        """Compare session type and connection attributes."""
        pass
