from threading import Thread

from cloudshell.cli.cli import Cli
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.cli.session_pool_manager import SessionPoolManager
from cloudshell.core.logger.qs_logger import get_qs_logger

CLI_MODE = CommandMode(r'%\s*$', '', 'exit', default_actions=lambda s: s.send_command('echo 123'))
DEFAULT_MODE = CommandMode(r'>\s*$', 'cli', 'exit', parent_mode=CLI_MODE,
                           default_actions=lambda s: s.send_command('set cli screen-length 0'))
CONFIG_MODE = CommandMode(r'#\s*$', 'configure', 'exit', parent_mode=DEFAULT_MODE)


def do_action(cli, session_type, mode, attrs):
    # session_type = SSHSession

    with cli.get_session(session_type, attrs, mode, cli.logger) as default_session:
        out = default_session.send_command('show version', error_map={'srx220h-poe': 'big error'})
        print(out)
        # with default_session.enter_mode(CONFIG_MODE) as config_session:
        #     out = config_session.send_command('show interfaces')
        #     print(out)
        # out = config_session.send_command('show interfaces', logger=cli.logger)
        # print(out)


if __name__ == '__main__':
    logger = get_qs_logger()
    pool = SessionPoolManager(max_pool_size=2)
    cli = Cli(logger=logger, session_pool=pool)
    connection_attrs = {
        'host': '192.168.28.150',
        'username': 'root',
        'password': 'Juniper'
    }

    connection_attrs1 = {
        'host': '192.168.28.150',
        'username': 'root',
        'password': 'Juniper1'
    }

    session_types = [TelnetSession, SSHSession]
    '''
    if context.session_type in session_types:
        session_type = session_types.get(context_session_type)
    else:
        session_type = session_types.values()
    '''
    # auto_session = [SSHSession, TelnetSession]
    # do_action(cli, session_types, DEFAULT_MODE, connection_attrs)
    Thread(target=do_action, args=(cli, SSHSession, DEFAULT_MODE, connection_attrs)).start()
    Thread(target=do_action, args=(cli, session_types, DEFAULT_MODE, connection_attrs)).start()
    # Thread(target=do_action, args=(cli, DEFAULT_MODE)).start()

    # config_vlan_mode = CommandMode(r'vlan#/s*$', 'config vlan', 'exit')
    #
    # with config_session.enter_mode(config_vlan_mode) as config_vlan_session:
    #     config_vlan_session.send_command('command')
    #
    # config_session.send_command('do th..')
