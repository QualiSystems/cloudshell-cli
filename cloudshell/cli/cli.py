from cloudshell.cli.session_handler import SessionHandler
from cloudshell.cli.session_state_wrapper import SessionModeWrapper
from logging import Logger
class Cli(object):
    SSH = 'ssh'
    TELNET = 'telnet'
    TCP = 'tcp'

    def __init__(self):


        self.logger = Logger('logger')

    def new_session(self,session_type,ip,default_state,port='',user='',password=''):
        session_handler = SessionHandler()
        session,connection_manager = session_handler.initiate_connection_manager(self.logger,session_type,ip,port,user,password,default_state)
        return SessionModeWrapper(session, connection_manager,default_state)


if __name__ == '__main__':
    #default_mode = Command_mode('[>$#]/s*$', 'enter', 'exit')
    from cloudshell.cli.cli import Cli
    from cloudshell.cli.prompt import Prompt
    import paramiko

    cli=Cli()
    default_state = Prompt('root@%', 'enter', 'exit')
    with cli.new_session(session_type=Cli.SSH,ip='192.168.28.150',user='root',password='Juniper', default_mode = default_state) as session:
        session.send_command('show version')
        session.change_mode()
