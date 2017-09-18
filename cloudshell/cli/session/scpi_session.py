import re
import socket

from cloudshell.cli.session.tcp_session import TCPSession


class SCPISession(TCPSession):
    SESSION_TYPE = 'SCPI'
    BUFFER_SIZE = 1024

    def __init__(self, host, port, on_session_start=None, *args, **kwargs):
        super(SCPISession, self).__init__(host, port, on_session_start, *args, **kwargs)

    def _initialize_session(self, prompt, logger):
        self._handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (self.host, self.port)
        self._handler.connect(server_address)
        self._handler.settimeout(self._timeout)

    def _connect_actions(self, prompt, logger):
        self._on_session_start(logger)

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
