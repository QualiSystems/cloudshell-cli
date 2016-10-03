from abc import ABCMeta, abstractmethod
from cloudshell.cli.session.session import Session


class SessionPool(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_session(self, session_type, **session_args):
        """
        Get session from pool
        :rtype Session
        """
        pass

    @abstractmethod
    def return_session(self, session):
        """
        Return session to pool
        :param session:
        :type session: Session
        """
        pass

    @abstractmethod
    def remove_session(self, session):
        """
        Remove session from pool
        :param session:
        :type session: Session
        """
        pass
