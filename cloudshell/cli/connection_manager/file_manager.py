import os

from qualipy.common.libs.connection_manager.session_manager import SessionManager


class FileManager(SessionManager):
    def __init__(self, filename=None, *args, **kwargs):
        SessionManager.__init__(self, **kwargs)

        self._filename = filename
        self._file = None
        self.removeFileIfExists(self._filename)

    def __del__(self):
        self.disconnect()

    def removeFileIfExists(self, file_name):
        file_path = os.path.dirname(file_name)

        if file_path and not os.path.exists(file_path):
            os.mkdir(file_path)

        elif os.path.exists(file_name):
            os.remove(file_name)

    def connect(self, expected_str=''):
        self._file = open(self._filename, 'a')

    def disconnect(self):
        self._file.close()

    def _send(self, command_string):
        command_string = command_string.replace('\r', '')
        self._file.write(command_string + "\n")
        self._file.flush()

    def _receive(self, timeout=None):
        return '>#'

    def hardwareExpect(self, cmd, expected_str=None, timeout=30, expected_map=None, retry_count=None):
        self.sendline(cmd)
        return 'Send'
