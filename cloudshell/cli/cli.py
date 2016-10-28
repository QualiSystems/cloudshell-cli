import logging

from cloudshell.cli.session_pool_context_manager import SessionPoolContextManager
from cloudshell.cli.session_pool_manager import SessionPoolManager
from cloudshell.cli.command_mode import CommandMode


class CLI(object):
    def __init__(self, session_pool=SessionPoolManager()):
        self._session_pool = session_pool

    def get_session(self, new_sessions, command_mode, logger=None):
        """
        Get session from the pool or create new
        :param new_sessions
        :param command_mode:
        :type command_mode: CommandMode
        :param logger:
        :type logger: Logger
        :return:
        :rtype: SessionPoolContextManager
        """
        if not isinstance(new_sessions, list):
            new_sessions = [new_sessions]

        if not logger:
            logger = logging.getLogger("cloudshell_cli")
        return SessionPoolContextManager(self._session_pool, new_sessions, command_mode, logger)
