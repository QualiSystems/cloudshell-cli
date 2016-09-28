from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.session_handler import SessionHandler
from cloudshell.cli.session_state_wrapper import SessionModeWrapper
from logging import Logger
class Cli(object):
    SSH = 'ssh'
    TELNET = 'telnet'
    TCP = 'tcp'

    def __init__(self):


        self.logger = Logger('logger')

    def get_session(self,session_type, connection_mode=None, **kwargs):
        session_handler = SessionHandler()
        session,connection_manager = session_handler.initiate_connection_manager(self.logger,session_type,ip,port,user,password)
        return SessionModeWrapper(session, connection_manager,default_state)


class CommandModeContainer(object):

    DEFAULT_MODE = CommandMode('default')
    CONFIG_MODE = CommandMode('config')
    VLAN_CONFIGURATION = CommandMode('vlan')
    DEFAULT_MODE.connect_mode(CONFIG_MODE)
    CONFIG_MODE.connect_mode(VLAN_CONFIGURATION)


if __name__ == '__main__':
    #default_mode = Command_mode('[>$#]/s*$', 'enter', 'exit')
    # from cloudshell.cli.cli import Cli
    from cloudshell.cli.prompt import Prompt
    import paramiko

    cli=Cli()
    default_state = Prompt('root@%', 'enter', 'exit')
    with cli.get_session(session_type=Cli.SSH,ip='192.168.28.150',user='root',password='Juniper', default_mode = CommandModeContainer.VLAN_CONFIGURATION) as session:
        with session.enter_mode(CommandMode('config t')) as config_mode_session:
            config_mode_session.sesnd_command('hddjjd')
        with ...
