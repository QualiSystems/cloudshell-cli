import traceback

import paramiko
from cloudshell.cli.session.expect_session import ExpectSession


class SSHSession(ExpectSession):
    SESSION_TYPE = 'SSH'

    def __init__(self, *args, **kwargs):
        ExpectSession.__init__(self, paramiko.SSHClient(), *args, **kwargs)

        self._handler.load_system_host_keys()
        self._handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self._port is None:
            self._port = 22

        self._current_channel = None

        self._buffer_size = 512
        if 'buffer_size' in kwargs:
            self._buffer_size = kwargs['buffer_size']

    def __del__(self):
        self.disconnect()

    def connect(self, prompt, logger):
        """Connect to device through ssh

        :param re_string: expected string in output
        :return: output
        """

        try:
            self._handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._handler.connect(self._host, self._port, self._username, self._password, timeout=self._timeout,
                                  banner_timeout=30, allow_agent=False, look_for_keys=False)
        except Exception as e:
            logger.error(traceback.format_exc())
            raise Exception('SSHSession', 'Failed to open connection to device: {0}'.format(e.message))

        self._current_channel = self._handler.invoke_shell()
        self._current_channel.settimeout(self._timeout)

        self.hardware_expect(None, expected_string=prompt, timeout=self._timeout, logger=logger)
        self._default_actions(logger)

    def disconnect(self):
        """Disconnect from device
        :return:
        """

        self._current_channel = None
        self._handler.close()

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
        return self._current_channel.recv(self._buffer_size)
