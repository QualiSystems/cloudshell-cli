from logging import Logger

from cloudshell.cli.command_mode_based_session_pool_context_manager import CommandModeBasedSessionPoolContextManager
from cloudshell.cli.session_pool_manager import SessionPoolManager

class Auth():

    def __init__(self,session_type,ip,username='',password='',port=''):
        self.session_type = session_type
        self.username = username
        self.password = password
        self.ip = ip
        self.port = port

class Cli(object):
    def __init__(self, session_pool=SessionPoolManager(), logger=Logger('Qualisystems')):
        self.logger = logger
        self._session_pool = session_pool

    def get_session(self, command_mode=None, auth = None, **session_attributes):
        """
        Get session from pool or create new
        :param session_attributes:
        :return:
        :rtype: SessionModeWrapper
        """
        return CommandModeBasedSessionPoolContextManager(self._session_pool, command_mode=command_mode,
                                                         auth=auth,**session_attributes)

    def get_thread_session(self, **session_attributes):
        """
        Get session from pool and keep it for current thread
        :param session_attributes:
        :return:
        """
        pass
