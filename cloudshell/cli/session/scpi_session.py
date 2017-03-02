import re
import socket

from cloudshell.cli.session.tcp_session import TCPSession


class SCPISession(TCPSession):
    SESSION_TYPE = 'SCPI'
    BUFFER_SIZE = 1024

    def __init__(self, host, port, on_session_start=None, *args, **kwargs):
        super(SCPISession, self).__init__(host, port, on_session_start=on_session_start, *args, **kwargs)

    def connect(self, prompt, logger):
        """
        Open connection to device / create session
        :param prompt:
        :param logger:
        :return:
        """

        if not self._handler:
            self._handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (self.host, self.port)
        self._handler.connect(server_address)
        self._handler.settimeout(self._timeout)

        if self.on_session_start and callable(self.on_session_start):
            self.on_session_start(self, logger)
        self._active = True

    def probe_for_prompt(self, expected_string, logger):
        return 'DUMMY_PROMPT'

    def hardware_expect(self, command, expected_string, logger, action_map=None, error_map=None, timeout=None,
                        retries=None, check_action_loop_detector=True, empty_loop_timeout=None,
                        remove_command_from_output=True, **optional_args):

        if ';:system:error?' not in command.lower():
            command += ';:system:error?'

        statusre = r'([-0-9]+), "(.*)"[\r\n]*$'

        remove_command_from_output = False  # avoid 'multiple repeat' error from '?' in the command - bug in expect_session

        rv = super(SCPISession, self).hardware_expect(command, statusre, logger, action_map, error_map, timeout,
                                                     retries, check_action_loop_detector, empty_loop_timeout,
                                                     remove_command_from_output, **optional_args)

        m = re.search(statusre, rv)
        if not m:
            raise Exception('SCPI status code not found in output: %s' % rv)

        code, message = m.groups()
        if code < 0:
            raise Exception('SCPI error: %d: %s' % (code, message))

        return rv
