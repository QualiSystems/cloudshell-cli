import logging
import socket
from io import StringIO
from typing import Optional

import paramiko
from scp import SCPClient

from cloudshell.cli.process.command.config import ProcessingConfig
from cloudshell.cli.session.core.config import SessionConfig
from cloudshell.cli.session.core.connection_params import ConnectionParams
from cloudshell.cli.session.core.session import Session
from cloudshell.cli.session.core.exception import SessionException, SessionReadTimeout, SessionReadEmptyData


class SSHSessionException(SessionException):
    pass


logger = logging.getLogger(__name__)


class SSHConfig(SessionConfig, ProcessingConfig):
    buffer_size: int = 512
    connect_timeout: int = 30


class SSHParams(ConnectionParams):
    def __init__(self, hostname, username, password=None, port=None, pkey=None, pkey_passphrase=None):
        super().__init__(hostname, port, username, password)
        self.pkey = pkey
        self.pkey_passphrase = pkey_passphrase

    def __eq__(self, other: "SSHParams"):
        return (super().__eq__(other)
                and self.pkey == other.pkey
                and self.pkey_passphrase == other.pkey_passphrase)


class SSHSession(Session):
    SESSION_TYPE = "SSH"

    def __init__(self, params: "SSHParams", config: Optional["SSHConfig"] = None):
        Session.__init__(self, params, config if config is not None else SSHConfig())
        self._handler = None
        self._current_channel = None

    def __eq__(self, other: "SSHSession"):
        """Is equal."""
        return isinstance(other, SSHSession) and self.params == other.params

    def __del__(self):
        self.disconnect()

    def _create_handler(self):
        self._handler = paramiko.SSHClient()
        self._handler.load_system_host_keys()
        self._handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self, timeout=None):
        """Initialize session.

        :param int timeout:
        :return:
        """
        connect_timeout = timeout or self.config.connect_timeout
        self._create_handler()
        try:
            self._handler.connect(
                self.hostname,
                self.port,
                self.username,
                self.password,
                timeout=connect_timeout,
                banner_timeout=30,
                allow_agent=False,
                look_for_keys=False,
                pkey=self._get_pkey_object(self.pkey, self.pkey_passphrase),
            )
        except Exception as e:
            logger.exception("Failed to initialize session:")
            raise SSHSessionException(
                "Failed to open connection to device: {}".format(e)
            )

        self._current_channel = self._handler.invoke_shell()
        self._current_channel.settimeout(connect_timeout)
        super(SSHSession, self).connect()

    def disconnect(self):
        """Disconnect from device."""
        if self._handler:
            self._handler.close()
        super(SSHSession, self).disconnect()

    def send(self, command):
        """Send message to device.

        :param str command:
        """
        if not self.get_connected():
            raise SessionException("Session is not connected")

        self._current_channel.send(command)

    def receive(self, timeout=None):
        """Read session buffer.

        :param int timeout: time between retries
        """

        if not self.get_connected():
            raise SessionException("Session is not connected")

        # Set the channel timeout
        timeout = timeout if timeout else self.config.timeout
        self._current_channel.settimeout(timeout)

        try:
            byte_data = self._current_channel.recv(self.config.buffer_size)
            data = byte_data.decode()
        except socket.timeout:
            raise SessionReadTimeout()

        if not data:
            raise SessionReadEmptyData()
        super(SSHSession, self).receive()

        return data

    def upload_scp(
            self, file_stream, dest_pathname, file_size=None, dest_permissions="0601"
    ):
        """Upload SCP.

        :param file_stream: filelike object: open file, StringIO, or other
            filelike object to read data from
        :param str dest_pathname: name of the file in the destination, with optional
            folder path prefix
        :param int file_size: size of the file, mandatory unless you are sure SFTP is
            available, in which case pass 0
        :param str dest_permissions: permission string as octal digits, e.g. 0601
        """
        scp = SCPClient(self._handler.get_transport())
        scp.putfo(
            fl=file_stream,
            remote_path=dest_pathname,
            mode=dest_permissions,
            size=file_size,
        )
        scp.close()

    def upload_sftp(
            self, file_stream, dest_pathname, file_size, dest_permissions="0601"
    ):
        """Upload SFTP.

        :param file_stream: filelike object: open file, StringIO, or other
            filelike object to read data from
        :param str dest_pathname: name of the file in the destination,
            with optional folder path prefix
        :param int file_size: size of the file, mandatory unless you are sure SFTP is
            available, in which case pass 0
        :param str dest_permissions: permission string as octal digits, e.g. 0601
        """
        sftp = paramiko.SFTPClient.from_transport(self._handler.get_transport())
        sftp.putfo(file_stream, dest_pathname)
        sftp.chmod(dest_pathname, int(dest_permissions, base=8))
        sftp.close()

    @staticmethod
    def _get_pkey_object(key_material, passphrase):
        """Try to detect private key type and return paramiko.PKey object."""
        for cls in [paramiko.RSAKey, paramiko.DSSKey, paramiko.ECDSAKey]:
            try:
                key = cls.from_private_key(StringIO(key_material), password=passphrase)
            except paramiko.ssh_exception.SSHException as e:
                # Invalid key, try other key type
                logger.warning(e)
            else:
                return key
