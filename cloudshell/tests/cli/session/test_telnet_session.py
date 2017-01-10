from unittest import TestCase
from cloudshell.cli.session.telnet_session import TelnetSession
from mock import Mock, patch


class TestTelnetSession(TestCase):
    def setUp(self):
        self._username = 'user'
        self._password = 'pass'
        self._hostname = 'hostname'
        self._port = 22
        self._on_session_start = Mock()

    @patch('cloudshell.cli.session.telnet_session.ExpectSession')
    @patch('cloudshell.cli.session.telnet_session.ConnectionParams')
    def test_init_attributes(self, connection_params, expect_session):
        self._instance = TelnetSession(self._hostname, self._username, self._password, port=self._port,
                                       on_session_start=self._on_session_start)
        mandatory_attributes = ['username', '_handler', 'password']
        self.assertEqual(len(set(mandatory_attributes).difference(set(self._instance.__dict__.keys()))), 0)

    @patch('cloudshell.cli.session.ssh_session.ExpectSession')
    def test_eq(self, expect_session):
        self._instance = TelnetSession(self._hostname, self._username, self._password, port=self._port,
                                       on_session_start=self._on_session_start)
        self.assertTrue(
            self._instance.__eq__(TelnetSession(self._hostname, self._username, self._password, port=self._port,
                                                on_session_start=self._on_session_start)))
        self.assertFalse(
            self._instance.__eq__(TelnetSession(self._hostname, 'incorrect_username', self._password, port=self._port,
                                                on_session_start=self._on_session_start)))
        self.assertFalse(
            self._instance.__eq__(TelnetSession(self._hostname, self._username, 'incorrect_password', port=self._port,
                                                on_session_start=self._on_session_start)))
