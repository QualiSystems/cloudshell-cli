from abc import ABCMeta, abstractmethod


class SessionManager(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def new_session(self, session_type, connection_attrs, prompt, logger):
        """
        Create new session with specific session type
        :param session_type:
        :param connection_attrs:
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
    def is_compatible(self, session, session_type, connection_attrs, logger):
        """
        Compare session type and connection attributes
        :param session:
        :param session_type:
        :param connection_attrs:
        :param logger:
        :return:
        """
        pass
