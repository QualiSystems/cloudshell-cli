import socket

import paramiko
from scp import SCPClient

from cloudshell.cli.session.connection_params import ConnectionParams
from cloudshell.cli.session.expect_session import ExpectSession
from cloudshell.cli.session.session_exceptions import (
    SessionException,
    SessionReadEmptyData,
    SessionReadTimeout,
)


class SSHSessionException(SessionException):
    pass


class SSHSession(ExpectSession, ConnectionParams):
    SESSION_TYPE = "SSH"
    BUFFER_SIZE = 512

    def __init__(
        self,
        host,
        username,
        password,
        port=None,
        on_session_start=None,
        pkey=None,
        *args,
        **kwargs
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

        self._handler = None
        self._current_channel = None
        self._buffer_size = self.BUFFER_SIZE

    def __eq__(self, other):
        """Is equal.

        :param SSHSession other:
        """
        return all(
            [
                ConnectionParams.__eq__(self, other),
                self.username == other.username,
                self.password == other.password,
                self.pkey == other.pkey,
            ]
        )

    def __del__(self):
        self.disconnect()

    def _create_handler(self):
        self._handler = paramiko.SSHClient()
        self._handler.load_system_host_keys()
        self._handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def _initialize_session(self, prompt, logger):
        """Initialize session.

        :param str prompt:
        :param logging.Logger logger:
        """
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
                pkey=self.pkey,
            )
        except Exception as e:
            logger.exception("Failed to initialize session:")
            raise SSHSessionException(
                "Failed to open connection to device: {}".format(e)
            )

        self._current_channel = self._handler.invoke_shell()
        self._current_channel.settimeout(self._timeout)

    def _connect_actions(self, prompt, logger):
        """Connect actions.

        :param str prompt:
        :param logging.Logger logger:
        """
        self.hardware_expect(
            None, expected_string=prompt, timeout=self._timeout, logger=logger
        )
        self._on_session_start(logger)

    def disconnect(self):
        """Disconnect from device."""
        if self._handler:
            self._handler.close()
        self._active = False

    def _send(self, command, logger):
        """Send message to device.

        :param str command:
        :param logging.Logger logger:
        """
        self._current_channel.send(command)

    def _receive(self, timeout, logger):
        """Read session buffer.

        :param int timeout: time between retries
        :param logging.Logger logger:
        """
        # Set the channel timeout
        timeout = timeout if timeout else self._timeout
        self._current_channel.settimeout(timeout)

        try:
            byte_data = self._current_channel.recv(self._buffer_size)
            data = byte_data.decode()
        except socket.timeout:
            raise SessionReadTimeout()

        if not data:
            raise SessionReadEmptyData()

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
