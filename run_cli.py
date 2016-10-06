from threading import Thread
from cloudshell.cli.cli import Cli
from cloudshell.cli.command_mode import CommandMode

from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.cli.cli import Auth
from cloudshell.cli.session.ssh_session import SSHSession


class CommandModeContainer(object):
    """
    Defined command modes
    """
    CLI_MODE = CommandMode(r'%\s*$', '', 'exit')
    DEFAULT_MODE = CommandMode(r'>\s*$', 'cli', 'exit', parent_mode=CLI_MODE,
                               default_actions=lambda session, logger: session.hardware_expect(
                                   command='set cli screen-length 0', expected_string=r'>\s*$', logger=logger))
    CONFIG_MODE = CommandMode(r'#\s*$', 'configure', 'exit', parent_mode=DEFAULT_MODE)


def do_action(cli):

    auth = Auth(host='192.168.28.150',username='root',password='Juniper',port=22)
    session = SSHSession

    with cli.get_session(session=session,auth=auth, logger=cli.logger,command_mode=CommandModeContainer.DEFAULT_MODE) as default_session:
        out = default_session.send_command('show interfaces', logger=cli.logger)
        print(out)
        with default_session.enter_mode(CommandModeContainer.CONFIG_MODE) as config_session:
            out = config_session.send_command('show interfaces', logger=cli.logger)
            print(out)
        out = config_session.send_command('show interfaces', logger=cli.logger)
        print(out)
    auth = Auth(host='192.168.28.150', username='root', password='Juniper', port=22)
    with cli.get_session(session=session,command_mode=CommandModeContainer.DEFAULT_MODE, auth=auth,
                         logger=cli.logger) as default_session:
        out = default_session.send_command('show interfaces', logger=cli.logger)
        print(out)

if __name__ == '__main__':
    logger = get_qs_logger()
    cli = Cli(logger=logger)
    do_action(cli)
    #Thread(target=do_action, args=(cli,)).start()
    #Thread(target=do_action, args=(cli,)).start()
    # Thread(target=do_action, args=(cli,)).start()

    # config_vlan_mode = CommandMode(r'vlan#/s*$', 'config vlan', 'exit')
    #
    # with config_session.enter_mode(config_vlan_mode) as config_vlan_session:
    #     config_vlan_session.send_command('command')
    #
    # config_session.send_command('do th..')