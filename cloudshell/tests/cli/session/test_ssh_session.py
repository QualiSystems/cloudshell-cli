from unittest import TestCase, skip
from cloudshell.cli.session.ssh_session import SSHSession
from mock import Mock, patch


class TestSshSession(TestCase):
    def setUp(self):
        self._username = 'user'
        self._password = 'pass'
        self._hostname = 'hostname'
        self._port = 22
        self._on_session_start = Mock()

    @patch('cloudshell.cli.session.ssh_session.ExpectSession')
    @patch('cloudshell.cli.session.ssh_session.ConnectionParams')
    def test_init_attributes(self, connection_params, expect_session):
        self._instance = SSHSession(self._hostname, self._username, self._password, port=self._port,
                                    on_session_start=self._on_session_start)
        mandatory_attributes = ['username', '_handler', '_current_channel', 'password', '_buffer_size']
        self.assertEqual(len(set(mandatory_attributes).difference(set(self._instance.__dict__.keys()))), 0)

    @patch('cloudshell.cli.session.ssh_session.ExpectSession')
    def test_eq(self, expect_session):
        self._instance = SSHSession(self._hostname, self._username, self._password, port=self._port,
                                    on_session_start=self._on_session_start)
        self.assertTrue(
            self._instance.__eq__(SSHSession(self._hostname, self._username, self._password, port=self._port,
                                             on_session_start=self._on_session_start)))
        self.assertFalse(
            self._instance.__eq__(SSHSession(self._hostname, 'incorrect_username', self._password, port=self._port,
                                             on_session_start=self._on_session_start)))
        self.assertFalse(
            self._instance.__eq__(SSHSession(self._hostname, self._username, 'incorrect_password', port=self._port,
                                             on_session_start=self._on_session_start)))
