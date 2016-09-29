from logging import Logger

from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.session_pool import SessionPool
from cloudshell.cli.session_pool_context_manager import SessionPoolContextManager


class Cli(object):
    SSH = 'ssh'
    TELNET = 'telnet'
    TCP = 'tcp'

    def __init__(self, session_pool):
        self.logger = Logger('logger')
        self._session_pool = session_pool

    # def get_session(self,session_type, connection_mode=None, **kwargs):
    #     session_handler = SessionHandler()
    #     session,connection_manager = session_handler.initiate_connection_manager(self.logger,session_type,ip,port,user,password)
    #     return SessionModeWrapper(session, connection_manager,default_state)

    def get_session(self, **session_attributes):
        return SessionPoolContextManager(self._session_pool, **session_attributes)


class CommandModeContainer(object):
    DEFAULT_MODE = CommandMode(r'[>]/s*$', '', 'exit')
    CONFIG_MODE = CommandMode(r'[#]/s*$', 'configure', 'exit')
    CONFIG_MODE.add_parent_mode(DEFAULT_MODE)
    # VLAN_CONFIGURATION = CommandMode('vlan')
    # DEFAULT_MODE.connect_mode(CONFIG_MODE)
    # CONFIG_MODE.connect_mode(VLAN_CONFIGURATION)


if __name__ == '__main__':
    cli = Cli(SessionPool())
    with cli.get_session(command_mode=CommandModeContainer.CONFIG_MODE, session_type=Cli.SSH, ip='192.168.28.150',
                         user='root', password='Juniper') as config_session:
        config_session.send_command('show ver')
        # with session.enter_mode(config_mode) as config_mode_session:
        #     config_mode_session.sesnd_command('hddjjd')
        # with ...
