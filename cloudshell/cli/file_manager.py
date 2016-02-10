import os

from cloudshell.cli.session_manager import SessionManager

class FileManager(SessionManager):
    @staticmethod
    def remove_file_if_exists(file_name):
        """
            Removing file from system if t exist
            :param file_name: name string
            :return:
        """
        file_path = os.path.dirname(file_name)

        if file_path and not os.path.exists(file_path):
            os.mkdir(file_path)

        elif os.path.exists(file_name):
            os.remove(file_name)

    def __init__(self, filename=None, *args, **kwargs):
        SessionManager.__init__(self, **kwargs)

        self._filename = filename
        self._file = None
        FileManager.remove_file_if_exists(self._filename)

    def __del__(self):
        self.disconnect()

    def connect(self, expected_str=''):
        """
            Conect to the device
            :param expected_str: regular expression string
            :return:
        """
        self._file = open(self._filename, 'a')

    def disconnect(self):
        """
            Disconnect from the device
            :return:
        """
        self._file.close()

    def _send(self, command_string):
        """
            Sending commnd to device

            :param command_string: command data string
            :return:
        """
        command_string = command_string.replace('\r', '')
        self._file.write(command_string + "\n")
        self._file.flush()

    def _receive(self, timeout=None):
        """
            Receive data from device

            :param timeout: time for waiting buffer
            :return:
        """
        return '>#'

    def hardware_expect(self, cmd, expected_str=None, timeout=30, expected_map=None, retry_count=None):
        """
            Sending data to device and then expecting specific prompt or
            string from output buffer

            :param cmd: command string
            :param expected_str: regular expression string
            :param timeout: time for waiting buffer
            :param expected_map: map of regular expression and associated callbacks
            :param retry_count: count of retries to read data from buffer

            :return:
        """
        self.sendline(cmd)
        return 'Send'
