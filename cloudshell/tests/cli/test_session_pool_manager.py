from unittest import TestCase

from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.session.ssh_session import SSHSession, SSHConnectionParams
from cloudshell.cli.session_pool_manager import SessionPoolManager
from cloudshell.cli.cli import CLI
from mock import Mock


def init_action(session):
    """
    :param Session session:
    :return:
    """
    print 'here'


class TestSessionPoolManager(TestCase):
    def setUp(self):
        self._session_manager = Mock()
        self._pool = Mock()
        self._session_pool_manager = SessionPoolManager(session_manager=self._session_manager, pool=self._pool)
        self._logger = Mock()
        self._session_type = Mock()
        self._connection_attrs = Mock()
        self._command_mode = Mock()
        self._prompt = Mock()


    def test_changing_a_session_param_will_create_a_new_session(self):
        cli = CLI()

        con_params = SSHConnectionParams("root","blah", 22, init_action )

        with cli.get_session(SSHSession, con_params, CommandMode(r'%\s*$')) as default_session:
            default_session.send_command('show version')


    def test_get_session_get_from_pool(self):
        self._pool.empty.return_value = False
        self._session_pool_manager._get_from_pool = Mock()
        session = self._session_pool_manager.get_session(self._session_type, self._connection_attrs, self._prompt,
                                                         self._logger)
        self._session_pool_manager._get_from_pool.assert_called_once_with(self._session_type, self._connection_attrs,
                                                                          self._prompt, self._logger)
