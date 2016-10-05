from abc import ABCMeta, abstractmethod
from cloudshell.cli.session.session import Session


class SessionPool(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_session(self, logger,auth, **session_args):
        """
        Get session from pool
        :rtype Session
        """
        pass

    @abstractmethod
    def return_session(self, session, logger):
        """
        Return session to pool
        :param session:
        :type session: Session
        """
        pass

    @abstractmethod
    def remove_session(self, session, logger):
        """
        Remove session from pool
        :param session:
        :type session: Session
        """
        pass
