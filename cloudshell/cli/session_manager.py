from abc import ABCMeta, abstractmethod


class SessionManager(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def new_session(self, new_sessions, prompt, logger):
        """
        Create new session with specific session type defined in sessions_params
        :param new_sessions
        :param prompt:
        :param logger:
        :return:
        """
        pass

    @abstractmethod
    def existing_sessions_count(self):
        """
        Count of existing sessions
        :return:
        :rtype: int
        """
        pass

    @abstractmethod
    def remove_session(self, session, logger):
        """
        remove session
        :param session:
        :param logger:
        :return:
        """
        pass

    @abstractmethod
    def is_compatible(self, session, new_sessions, logger):
        """
        Compare session type and connection attributes
        :param session:
        :param new_sessions
        :param logger:
        :return:
        """
        pass
