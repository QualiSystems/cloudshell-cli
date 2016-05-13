__author__ = 'g8y3e'

import paramiko
import inject
from cloudshell.cli.session.expect_session import ExpectSession


class SSHSession(ExpectSession):
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

    @inject.params(logger='logger')
    def connect(self, re_string='', logger=None):
        """
            Connect to device through ssh
            :param re_string: regular expression of end of output
            :return: str
        """
        logger.info("Host: {0}, port: {1}, username: {2}, password: {3}, timeout: {4}".
                    format(self._host, self._port, self._username, self._password, self._timeout))

        self._handler.connect(self._host, self._port, self._username, self._password, timeout=self._timeout,
                              banner_timeout=30, allow_agent=False, look_for_keys=False)

        self._current_channel = self._handler.invoke_shell()
        self._current_channel.settimeout(self._timeout)

        output = self.hardware_expect(re_string=re_string, timeout=self._timeout)
        self._default_actions()
        logger.info(output)

        return output

    # @inject.params(logger='logger')
    def disconnect(self, logger=None):
        """
            Disconnect from device
            :return:
        """
        # logger.info('Disconnected from device!')
        self._current_channel = None
        self._handler.close()

    def _send(self, data_str):
        """
            Send data to device

            :param data_str: command string
            :return:
        """
        self._current_channel.send(data_str)

    def _receive(self, timeout=None):
        """
            Read data from device
            :param timeout: time between retries
            :return: str
        """
        # Set the channel timeout
        timeout = timeout if timeout else self._timeout
        self._current_channel.settimeout(timeout)
        return self._current_channel.recv(self._buffer_size)
