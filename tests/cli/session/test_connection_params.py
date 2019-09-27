from unittest import TestCase

from cloudshell.cli.session.connection_params import ConnectionParams

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class ConnectionParamsTestImpl(ConnectionParams):
    pass


class TestConnectionParams(TestCase):
    def setUp(self):
        self._hostname = "host"
        self._port = 22
        self._on_session_start = Mock()

    def test_init_attributes(self):
        instance = ConnectionParamsTestImpl(
            self._hostname, port=self._port, on_session_start=self._on_session_start
        )
        mandatory_attributes = ["host", "on_session_start", "port"]
        self.assertEqual(
            len(set(mandatory_attributes).difference(set(instance.__dict__.keys()))), 0
        )

    def test_init_port_not_int(self):
        exception = ValueError
        with self.assertRaises(exception):
            ConnectionParamsTestImpl(
                self._hostname, port="port", on_session_start=self._on_session_start
            )

    def test_init_split_host(self):
        instance = ConnectionParamsTestImpl(
            self._hostname + ":" + str(self._port),
            port=None,
            on_session_start=self._on_session_start,
        )
        self.assertEqual(instance.port, self._port)

    def test_eq(self):
        instance = ConnectionParamsTestImpl(
            self._hostname, port=self._port, on_session_start=self._on_session_start
        )
        self.assertTrue(
            instance.__eq__(
                ConnectionParamsTestImpl(
                    self._hostname,
                    port=self._port,
                    on_session_start=self._on_session_start,
                )
            )
        )
        self.assertFalse(
            instance.__eq__(
                ConnectionParamsTestImpl(
                    "incorrect_host",
                    port=self._port,
                    on_session_start=self._on_session_start,
                )
            )
        )
        self.assertFalse(
            instance.__eq__(
                ConnectionParamsTestImpl(
                    self._hostname, port="44", on_session_start=self._on_session_start
                )
            )
        )
