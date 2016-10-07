from logging import Logger

from cloudshell.cli.session_pool_context_manager import SessionPoolContextManager
from cloudshell.cli.session_pool_manager import SessionPoolManager


class Cli(object):
    def __init__(self, session_pool=SessionPoolManager(), logger=Logger('Qualisystems')):
        self.logger = logger
        self._session_pool = session_pool

    def get_session(self, session_type, connection_attrs, command_mode, logger):
        """
        Get session from pool or create new
        :param session_attributes:
        :return:
        :rtype: SessionModeWrapper
        """

        return SessionPoolContextManager(self._session_pool, session_type, connection_attrs, command_mode, logger)

    def get_thread_session(self, **session_attributes):
        """
        Get session from pool and keep it for current thread
        :param session_attributes:
        :return:
        """
        pass
