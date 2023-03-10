from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

import paramiko
from scp import SCPClient

from cloudshell.cli.session.connection_params import ConnectionParams
from cloudshell.cli.session.expect_session import ExpectSession
from cloudshell.cli.session.session_exceptions import SessionException

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.types import T_ON_SESSION_START, T_TIMEOUT


class SSHSessionException(SessionException):
    pass


class SSHSession(ExpectSession, ConnectionParams):
    SESSION_TYPE = "SSH"
    BUFFER_SIZE = 512

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int | None = None,
        on_session_start: T_ON_SESSION_START | None = None,
        pkey: str | None = None,
        pkey_passphrase: str | None = None,
        *args,
        **kwargs,
    ):
        ConnectionParams.__init__(
            self, host, port=port, on_session_start=on_session_start, pkey=pkey
        )
        ExpectSession.__init__(self, *args, **kwargs)

        if self.port is None:
            self.port = 22

        self.username = username
        self.password = password
        self.pkey = pkey
        self.pkey_passphrase = pkey_passphrase

        self._handler = None
        self._current_channel = None
        self._buffer_size = self.BUFFER_SIZE

    def __eq__(self, other) -> bool:
        return all(
            [
                ConnectionParams.__eq__(self, other),
                self.username == other.username,
                self.password == other.password,
                self.pkey == other.pkey,
                self.pkey_passphrase == other.pkey_passphrase,
            ]
        )

    def __del__(self) -> None:
        self.disconnect()

    def _create_handler(self) -> None:
        self._handler = paramiko.SSHClient()
        self._handler.load_system_host_keys()
        self._handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def _initialize_session(self, prompt: str, logger: Logger) -> None:
        self._create_handler()
        try:
            self._handler.connect(
                self.host,
                self.port,
                self.username,
                self.password,
                timeout=self._timeout,
                banner_timeout=30,
                allow_agent=False,
                look_for_keys=False,
                pkey=self._get_pkey_object(self.pkey, self.pkey_passphrase, logger),
            )
        except Exception as e:
            logger.exception("Failed to initialize session:")
            raise SSHSessionException(f"Failed to open connection to device: {e}")

        self._current_channel = self._handler.invoke_shell()
        self._current_channel.settimeout(self._timeout)

    def _connect_actions(self, prompt: str, logger: Logger) -> None:
        self.hardware_expect(
            None, expected_string=prompt, timeout=self._timeout, logger=logger
        )
        self._on_session_start(logger)

    def disconnect(self) -> None:
        """Disconnect from device."""
        if self._handler:
            self._handler.close()
        self._active = False

    def _send(self, command: str, logger: Logger) -> None:
        """Send message to device."""
        self._current_channel.send(command)

    def _set_timeout(self, timeout: T_TIMEOUT) -> None:
        self._current_channel.settimeout(timeout)

    def _read_byte_data(self) -> bytes:
        return self._current_channel.recv(self._buffer_size)

    @property
    def scp_client(self) -> SCPClient:
        return SCPClient(self._handler.get_transport())

    @property
    def sftp_client(self) -> paramiko.SFTPClient:
        return paramiko.SFTPClient.from_transport(self._handler.get_transport())

    @staticmethod
    def _get_pkey_object(
        key_material: str | None, passphrase: str | None, logger: Logger
    ) -> paramiko.RSAKey | paramiko.DSSKey | paramiko.ECDSAKey | None:
        """Try to detect private key type and return paramiko.PKey object."""
        if not key_material:
            return None

        for cls in [paramiko.RSAKey, paramiko.DSSKey, paramiko.ECDSAKey]:
            try:
                key = cls.from_private_key(StringIO(key_material), password=passphrase)
            except paramiko.ssh_exception.SSHException as e:
                # Invalid key, try other key type
                logger.warning(e)
            else:
                return key
