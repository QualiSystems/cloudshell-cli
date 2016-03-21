__author__ = 'g8y3e'

import paramiko

from cloudshell.cli.old.session_manager import SessionManager

class SSHManager(SessionManager):
    def __init__(self, *args, **kwargs):
        SessionManager.__init__(self, paramiko.SSHClient(), *args, **kwargs)
        self._handler.load_system_host_keys()
        self._handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self._port is None:
            self._port = 22

        self._current_channel = None
        self._buffer_size = 8192

    def __del__(self):
        self.disconnect()

    def connect(self, expected_str=''):
        """
            Connect to device through ssh
            :param expected_str: regular expration of end of output
            :return: str
        """
        SessionManager.connect(self, expected_str)
        self._logger.info("Host: {0}, port: {1}, username: {2}, password: {3}, timeout: {4}".format(self._host,
                                                    self._port, self._username, self._password, self._timeout))
        self._handler.connect(self._host, self._port, self._username, self._password, timeout=self._timeout,
                              banner_timeout=30, allow_agent=False, look_for_keys=False)

        self._current_channel = self._handler.invoke_shell()
        self._current_channel.settimeout(self._timeout)

        output = self._read_start_up_buffer(expected_str, timeout=self._timeout)
        self._logger.info(output)

        return output

    def disconnect(self):
        """
            Disconnect from device
            :return:
        """
        self._logger.info("Disconnect")
        self._current_channel = None
        self._handler.close()

    def _send(self, command_string):
        """
            Send data to device

            :param command_string: commnad string
            :return:
        """
        self._current_channel.send(command_string)

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

