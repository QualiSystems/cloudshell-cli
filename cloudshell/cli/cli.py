from cloudshell.cli.session_pool_context_manager import SessionPoolContextManager
from cloudshell.cli.session_pool_manager import SessionPoolManager
from cloudshell.cli.session.session import Session
from cloudshell.cli.command_mode import CommandMode


class Cli(object):
    def __init__(self, session_pool=SessionPoolManager()):
        self._session_pool = session_pool

    def get_session(self, session_type, connection_attrs, command_mode, logger):
        """
        Get session from the pool or create new
        :param session_type:
        :type session_type: Session
        :param connection_attrs:
        :type connection_attrs: dict
        :param command_mode:
        :type command_mode: CommandMode
        :param logger:
        :type logger: Logger
        :return:
        :rtype: SessionPoolContextManager
        """

        return SessionPoolContextManager(self._session_pool, session_type, connection_attrs, command_mode, logger)
