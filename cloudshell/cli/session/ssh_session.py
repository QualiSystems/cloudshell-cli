import os
import socket
import traceback
from StringIO import StringIO

from paramiko import RSAKey

from scpclient import Write

from cloudshell.cli.session.session_exceptions import SessionException, SessionReadTimeout, SessionReadEmptyData
import paramiko
from cloudshell.cli.session.connection_params import ConnectionParams
from cloudshell.cli.session.expect_session import ExpectSession


class SSHSessionException(SessionException):
    pass


class SSHSession(ExpectSession, ConnectionParams):
    SESSION_TYPE = 'SSH'
    BUFFER_SIZE = 512

    def __init__(self, host, username, password, port=None, on_session_start=None, pkey=None, *args, **kwargs):
        ConnectionParams.__init__(self, host, port=port, on_session_start=on_session_start, pkey=pkey)
        ExpectSession.__init__(self, *args, **kwargs)

        if hasattr(self, 'port') and self.port is None:
            self.port = 22

        self.username = username
        self.password = password
        self.pkey = pkey

        self._handler = None
        self._current_channel = None
        self._buffer_size = self.BUFFER_SIZE

    def __eq__(self, other):
        """
        :param other:
        :type other: SSHSession
        :return:
        """
        return ConnectionParams.__eq__(self,
                                       other) and \
               self.username == other.username and \
               self.password == other.password and \
               self.pkey == other.pkey

    def __del__(self):
        self.disconnect()

    def _create_handler(self):
        self._handler = paramiko.SSHClient()
        self._handler.load_system_host_keys()
        self._handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def _initialize_session(self, prompt, logger):
        self._create_handler()
        try:
            self._handler.connect(self.host, self.port, self.username, self.password, timeout=self._timeout,
                                  banner_timeout=30, allow_agent=False, look_for_keys=False, pkey=self.pkey)
        except Exception as e:
            logger.error(traceback.format_exc())
            raise SSHSessionException(self.__class__.__name__,
                                      'Failed to open connection to device: {0}'.format(e.message))

        self._current_channel = self._handler.invoke_shell()
        self._current_channel.settimeout(self._timeout)

    def _connect_actions(self, prompt, logger):
        self.hardware_expect(None, expected_string=prompt, timeout=self._timeout, logger=logger)
        self._on_session_start(logger)

    def disconnect(self):
        """Disconnect from device
        :return:
        """

        # self._current_channel = None
        if self._handler:
            self._handler.close()
        self._active = False

    def _send(self, command, logger):
        """Send message to device

        :param data_str:  message/command
        :return:
        """

        self._current_channel.send(command)

    def _receive(self, timeout, logger):
        """Read session buffer

        :param timeout: time between retries
        :return:
        """

        # Set the channel timeout
        timeout = timeout if timeout else self._timeout
        self._current_channel.settimeout(timeout)

        try:
            data = self._current_channel.recv(self._buffer_size)
        except socket.timeout:
            raise SessionReadTimeout()

        if not data:
            raise SessionReadEmptyData()

        return data

    def upload_scp(self, file_stream, dest_pathname, file_size, dest_permissions='0601'):
        """

        :param file_stream: filelike object : open file, StringIO, or other filelike object to read data from
        :param dest_pathname: str : name of the file in the destination, with optional folder path prefix
        :param file_size: int : size of the file, mandatory unless you are sure SFTP is available, in which case pass 0
        :param dest_permissions: str : permission string as octal digits, e.g. 0601
        :return:
        """
        folder = os.path.dirname(dest_pathname)
        file_name = os.path.basename(dest_pathname)
        scp = Write(self._handler.get_transport(), folder)
        scp.send(file_stream, file_name, dest_permissions, file_size)

    def upload_sftp(self, file_stream, dest_pathname, file_size, dest_permissions='0601'):
        """

        :param file_stream: filelike object : open file, StringIO, or other filelike object to read data from
        :param dest_pathname: str : name of the file in the destination, with optional folder path prefix
        :param file_size: int : size of the file, mandatory unless you are sure SFTP is available, in which case pass 0
        :param dest_permissions: str : permission string as octal digits, e.g. 0601
        :return:
        """
        sftp = paramiko.SFTPClient.from_transport(self._handler.get_transport())
        sftp.putfo(file_stream, dest_pathname)
        sftp.chmod(dest_pathname, int(dest_permissions, base=8))
        sftp.close()
