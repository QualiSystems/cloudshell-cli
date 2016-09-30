from logging import Logger

from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.session_pool import SessionPool
from cloudshell.cli.session_mode_wrapper import SessionModeWrapper
from cloudshell.cli.session_pool_context_manager import SessionPoolContextManager


class Cli(object):
    SSH = 'ssh'
    TELNET = 'telnet'
    TCP = 'tcp'

    def __init__(self, session_pool):
        self.logger = Logger('logger')
        self._session_pool = session_pool

    def get_session(self, **session_attributes):
        """
        Get session from pool or create new
        :param session_attributes:
        :return:
        :rtype: SessionModeWrapper
        """
        return SessionPoolContextManager(self._session_pool, **session_attributes)

    def get_thread_session(self, **session_attributes):
        """
        Get session from pool and keep it for current thread
        :param session_attributes:
        :return:
        """
        pass


class CommandModeContainer(object):
    """
    Defined command modes
    """
    DEFAULT_MODE = CommandMode(r'>/s*$', '', 'exit')
    CONFIG_MODE = CommandMode(r'#/s*$', 'configure', 'exit', parent_mode=DEFAULT_MODE)
    TEST_MODE = CommandMode(r'[$>#]/s*$', 'test', 'exit', parent_mode=CONFIG_MODE)


if __name__ == '__main__':
    session_pool = SessionPool()
    cli = Cli(session_pool)
    with cli.get_session(command_mode=CommandModeContainer.CONFIG_MODE, session_type=Cli.SSH, ip='192.168.28.150',
                         user='root', password='Juniper') as config_session:
        config_session.send_command('show ver')

        config_vlan_mode = CommandMode(r'vlan#/s*$', 'config vlan', 'exit')

        with config_session.enter_mode(config_vlan_mode) as config_vlan_session:
            config_vlan_session.send_command('command')

        config_session.send_command('do th..')
