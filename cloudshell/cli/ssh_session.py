__author__ = 'g8y3e'

import paramiko

from cloudshell.cli.expect_session import ExpectSession

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

    def connect(self, re_string=''):
        """
            Connect to device through ssh
            :param re_string: regular expration of end of output
            :return: str
        """
        self._logger.info("Host: {0}, port: {1}, username: {2}, password: {3}, timeout: {4}".
                          format(self._host, self._port, self._username, self._password, self._timeout))

        self._handler.connect(self._host, self._port, self._username, self._password, timeout=self._timeout,
                              banner_timeout=30, allow_agent=False, look_for_keys=False)

        self._current_channel = self._handler.invoke_shell()
        self._current_channel.settimeout(self._timeout)

        output = self.hardware_expect('', re_string=re_string, timeout=self._timeout)
        self._logger.info(output)

        return output

    def disconnect(self):
        """
            Disconnect from device
            :return:
        """
        self._logger.info('Disconnected from device!')
        self._current_channel = None
        self._handler.close()

    def _send(self, data_str):
        """
            Send data to device

            :param data_str: commnad string
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

if __name__ == "__main__":

    from collections import OrderedDict
    from cloudshell.core.logger.qs_logger import get_qs_logger

    logger = get_qs_logger()

    session = SSHSession(username='root', password='Password1', host='192.168.42.235', logger=logger)
    #session = SSHSession(username='klop', password='azsxdc', host='192.168.42.193', logger=logger, timeout=2)

    prompt = '[$#] *$'

    session.connect(prompt)

    actions = OrderedDict()
    actions["--[Mm]ore--"] = lambda: session.send_line('')

    output = session.hardware_expect('cd /', re_string=prompt, expect_map=actions)
    output = session.hardware_expect('ls', re_string=prompt, expect_map=actions)
    output = output

