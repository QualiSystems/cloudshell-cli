from cloudshell.cli.session_pool_context_manager import SessionPoolContextManager
from cloudshell.cli.session_pool_manager import SessionPoolManager
from cloudshell.cli.session.session import Session
from cloudshell.cli.command_mode import CommandMode
import logging

class BaseCLIConnectionParams(object):
    def __init__(self, port, on_session_start=None):
        """
        :param int port: The port to use for the connection
        :param (Session) -> None on_session_start: Callback function to be triggered after the CLI session starts allows
         running common initialization commands
        """
        self.port = port
        self.on_session_start = on_session_start

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.port == other.port


class CLI(object):
    def __init__(self, session_pool=SessionPoolManager()):
        self._session_pool = session_pool

    def get_session(self, session_type, connection_attrs, command_mode, logger=None):
        """
        Get session from the pool or create new
        :param session_type:
        :type session_type: Session
        :param connection_attrs:
        :type connection_attrs: BaseCLIConnectionParams
        :param command_mode:
        :type command_mode: CommandMode
        :param logger:
        :type logger: Logger
        :return:
        :rtype: SessionPoolContextManager
        """

        if not logger:
            logger = logging.getLogger("cloudshell_cli")
        return SessionPoolContextManager(self._session_pool, session_type, connection_attrs, command_mode, logger)
