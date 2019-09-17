from unittest import TestCase

from cloudshell.cli.session.telnet_session import TelnetSession

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestTelnetSession(TestCase):
    def setUp(self):
        self._username = "user"
        self._password = "pass"
        self._hostname = "hostname"
        self._port = 22
        self._on_session_start = Mock()

    @patch("cloudshell.cli.session.telnet_session.ExpectSession")
    @patch("cloudshell.cli.session.telnet_session.ConnectionParams")
    def test_init_attributes(self, connection_params, expect_session):
        self._instance = TelnetSession(
            self._hostname,
            self._username,
            self._password,
            port=self._port,
            on_session_start=self._on_session_start,
        )
        mandatory_attributes = ["username", "_handler", "password"]
        self.assertEqual(
            len(
                set(mandatory_attributes).difference(
                    set(self._instance.__dict__.keys())
                )
            ),
            0,
        )

    @patch("cloudshell.cli.session.ssh_session.ExpectSession")
    def test_eq(self, expect_session):
        self._instance = TelnetSession(
            self._hostname,
            self._username,
            self._password,
            port=self._port,
            on_session_start=self._on_session_start,
        )
        self.assertTrue(
            self._instance.__eq__(
                TelnetSession(
                    self._hostname,
                    self._username,
                    self._password,
                    port=self._port,
                    on_session_start=self._on_session_start,
                )
            )
        )
        self.assertFalse(
            self._instance.__eq__(
                TelnetSession(
                    self._hostname,
                    "incorrect_username",
                    self._password,
                    port=self._port,
                    on_session_start=self._on_session_start,
                )
            )
        )
        self.assertFalse(
            self._instance.__eq__(
                TelnetSession(
                    self._hostname,
                    self._username,
                    "incorrect_password",
                    port=self._port,
                    on_session_start=self._on_session_start,
                )
            )
        )

    @patch("cloudshell.cli.session.telnet_session.telnetlib")
    def test_intialize_session(self, telnet_lib):
        # Setup
        telnet_mock = Mock()
        telnet_lib.Telnet.return_value = telnet_mock
        hostname = "localhost"
        self._instance = TelnetSession(
            hostname,
            self._username,
            "incorrect_password",
            port=self._port,
            on_session_start=self._on_session_start,
        )

        # Act
        self._instance._initialize_session(">", logger=Mock())

        # Assert
        self.assertIsNotNone(self._instance._handler)
        self.assertEqual(telnet_mock, self._instance._handler)

    def test_connect_actions(self):
        # Setup
        hostname = "localhost"
        on_session_start = Mock()
        self._instance = TelnetSession(
            hostname,
            self._username,
            "password",
            port=self._port,
            on_session_start=on_session_start,
        )
        self._instance._timeout = 0
        self._instance.hardware_expect = Mock(return_value="Done")
        self._instance._handler = Mock()

        # Act
        self._instance._connect_actions(">", logger=Mock())

        # Assert
        self._instance.hardware_expect.assert_called_once()
        on_session_start.assert_called_once()
