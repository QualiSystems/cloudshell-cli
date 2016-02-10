__author__ = 'g8y3e'
import traceback

import paramiko

from qualipy.common.libs.connection_manager.session_manager import SessionManager


class SSHManager(SessionManager):

    def __init__(self, *args, **kwargs):
        SessionManager.__init__(self, paramiko.SSHClient(), *args, **kwargs)
        self._handler.load_system_host_keys()
        self._handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self._port is None:
            self._port = 22

        self._current_channel = None
        self._buffer_size = 512

    def __del__(self):
        self.disconnect()

    def connect(self, expected_str=''):
        SessionManager.connect(self, expected_str)
        #try:
        self._logger.info("Host: {0}, port: {1}, username: {2}, password: {3}, timeout: {4}".format(self._host,
                                                    self._port, self._username, self._password, self._timeout))
        self._handler.connect(self._host, self._port,
                              self._username, self._password, timeout=self._timeout, banner_timeout=30)

        self._current_channel = self._handler.invoke_shell()
        self._current_channel.settimeout(self._timeout)

        output = self._readStartUpBuffer(expected_str, timeout=self._timeout)
        self._logger.info(output)

       #except Exception, err:
       #    error_str = "Exception: " + str(err) + '\n'

       #    error_str += '-' * 60 + '\n'
       #    error_str += traceback.format_exc()
       #    error_str += '-' * 60
       #    if self._logger:
       #        self._logger.error(error_str)

       #    raise Exception('SSH Manager', error_str)

        return output

    def disconnect(self):
        self._logger.info("Disconnect")
        self._current_channel = None
        self._handler.close()

    def _send(self, command_string):
        self._current_channel.send(command_string)

    def _receive(self, timeout=None):
        # Set the channel timeout
        timeout = timeout if timeout else self._timeout
        self._current_channel.settimeout(timeout)
        return self._current_channel.recv(self._buffer_size)

