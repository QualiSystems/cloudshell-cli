from cloudshell.cli.cli import CLI
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session_pool_manager import SessionPoolManager
from cloudshell.core.logger.qs_logger import get_qs_logger


class CliCommandMode(CommandMode):
    PROMPT = r'$'
    ENTER_COMMAND = ''
    EXIT_COMMAND = 'exit'

    def __init__(self,context):

        CommandMode.__init__(self, CliCommandMode.PROMPT, CliCommandMode.ENTER_COMMAND,
                             CliCommandMode.EXIT_COMMAND)


LOGGER = get_qs_logger()

CommandMode.RELATIONS_DICT = {
    CliCommandMode: {}
}
if __name__ == '__main__':
    pool = SessionPoolManager(max_pool_size=1)
    cli = CLI(session_pool=pool)

    context = type('context', (object,), {'resource': type('resource', (object,), {'name': 'test name'})})

    host = '<IP>'
    username = '<username>'
    password = '<pass>'

    session = SSHSession(host, username, password)
    modes = CommandModeHelper.create_command_mode(context)
    default_mode = modes[CliCommandMode]

    with cli.get_session(session, default_mode) as default_session:
        out = default_session.send_command('echo Cli Demo connected to Ubuntu Machine')
        print(out)
        fd = open('C:\\Users\\luiza.n\\Downloads\\readfrom.txt')
        default_session.session.upload_scp(fd, './target.txt', 3104, '0666')




'''
cli = get_cli(session_pool_size)  # in initialize
handler = MyCliHandler(cli, context, logger, api)  # in the runner
flow = MyFlow(cli_handler=handler)
with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as session:  # in execute_flow()
    session.session.scp_upload(fd, 'target.bin', size, '0666')
'''