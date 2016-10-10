from logging import Logger

from cloudshell.cli.session_pool_context_manager import SessionPoolContextManager
from cloudshell.cli.session_pool_manager import SessionPoolManager


class Cli(object):
    def __init__(self, session_pool=SessionPoolManager(), logger=Logger('Qualisystems')):
        self.logger = logger
        self._session_pool = session_pool

    def get_session(self, session_type, connection_attrs, command_mode, logger):
        """

        :param session_type:
        :param connection_attrs:
        :param command_mode:
        :param logger:
        :return:
        :rtype: SessionPoolContextManager
        """

        return SessionPoolContextManager(self._session_pool, session_type, connection_attrs, command_mode, logger)

    def get_thread_session(self, **session_attributes):
        """
        Get session from pool and keep it for current thread
        :param session_attributes:
        :return:
        """
        pass
