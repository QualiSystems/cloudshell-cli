import unittest
from cloudshell.cli.cli import CLI
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session_pool_manager import SessionPoolManager


class CreateSessionTestCases(unittest.TestCase):

    def test_create_session(self):

        pool = SessionPoolManager(max_pool_size=1)
        cli = CLI(session_pool=pool)

        connection_attrs = {
            'host': '192.168.28.150',
            'username': 'root',
            'password': 'Juniper'
        }

        with cli.get_session(SSHSession, attrs, mode, LOGGER, ) as default_session:
            # out = default_session.send_command('show version', error_map={'srx220h-poe': 'big error'})
            out = default_session.send_command('show version')
            print(out)
            # config_command_mode = ConfigCommandMode(context)
            # config_command_mode.add_parent_mode(mode)
            # with default_session.enter_mode(config_command_mode) as config_session:
            #     out = config_session.send_command('show interfaces')
            #     print(out)
            #     out = config_session.send_command('show interfaces', logger=cli.logger)
            #     print(out)

if __name__ == '__main__':
    unittest.main()
