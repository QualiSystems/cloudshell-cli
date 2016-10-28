import socket
import time
from collections import OrderedDict

from abc import ABCMeta
from cloudshell.cli.session.session_exceptions import SessionLoopDetectorException, SessionLoopLimitException
import re
from cloudshell.cli.session.session import Session
from cloudshell.cli.helper.normalize_buffer import normalize_buffer
from cloudshell.cli.service.cli_exceptions import CommandExecutionException


class ExpectSession(Session):
    """
    Help to handle additional actions during send command
    """

    __metaclass__ = ABCMeta

    SESSION_TYPE = 'EXPECT'

    MAX_LOOP_RETRIES = 20
    READ_TIMEOUT = 30
    EMPTY_LOOP_TIMEOUT = 0.2
    CLEAR_BUFFER_TIMEOUT = 0.1
    LOOP_DETECTOR_MAX_ACTION_LOOPS = 3
    LOOP_DETECTOR_MAX_COMBINATION_LENGTH = 4
    '''
    def __init__(self, handler=None, username=None, password=None, host=None, port=None,
                 timeout=None, new_line='\r', logger=None, config=None, default_actions=None, **kwargs):
    '''

    def __init__(self, handler=None, host=None, port=None, username=None, password=None, timeout=READ_TIMEOUT,
                 new_line='\r', default_actions=None, max_loop_retries=MAX_LOOP_RETRIES,
                 empty_loop_timeout=EMPTY_LOOP_TIMEOUT,
                 loop_detector_max_action_loops=LOOP_DETECTOR_MAX_ACTION_LOOPS,
                 loop_detector_max_combination_length=LOOP_DETECTOR_MAX_COMBINATION_LENGTH,
                 clear_buffer_timeout=CLEAR_BUFFER_TIMEOUT, logger=None):
        """

        :param handler:
        :param username:
        :param password:
        :param host:
        :param port:
        :param timeout:
        :param new_line:
        :param kwargs:
        :return:
        """

        self._handler = handler
        self._port = None
        if port and int(port) > 0:
            self._port = int(port)
        if host:
            temp_host = host.split(':')
            self._host = temp_host[0]
            if not self._port and len(temp_host) > 1:
                self._port = int(temp_host[1])
        else:
            self._host = host

        self._username = username
        self._password = password

        self._new_line = new_line
        self._timeout = timeout

        self._default_actions_func = default_actions

        self._max_loop_retries = max_loop_retries
        self._empty_loop_timeout = empty_loop_timeout

        self._loop_detector_max_action_loops = loop_detector_max_action_loops
        self._loop_detector_max_combination_length = loop_detector_max_combination_length
        self._clear_buffer_timeout = clear_buffer_timeout
        self._timeout = timeout

    @property
    def session_type(self):
        return self.SESSION_TYPE

    def _receive_with_retries(self, timeout, retries_count):
        """Read session buffer with several retries

        :param timeout:
        :param retries_count:
        :return:
        """

        current_retries = 0
        current_output = None

        while current_retries < retries_count:
            current_retries += 1

            try:
                current_output = self._receive(timeout)
                if current_output == '':
                    time.sleep(0.5)
                    continue
            except socket.timeout:
                time.sleep(0.5)
                continue
            except timeout:
                break
            except Exception as err:
                raise err
            break

        if current_output is None:
            raise Exception('ExpectSession', 'Failed to get response from device')
        return current_output

    def _clear_buffer(self, timeout, logger):
        """
        Clear buffer

        :param timeout:
        :return:
        """
        out = ''
        while True:
            try:
                read_buffer = self._receive(timeout, logger)
            except socket.timeout:
                read_buffer = None
            if read_buffer:
                out += read_buffer
            else:
                break
        return out

    def send_line(self, command, logger):
        """
        Add new line to the end of command string and send

        :param command:
        :return:
        """
        self._send(command + self._new_line, logger)

    def hardware_expect(self, command, expected_string, logger, action_map=OrderedDict(), error_map=OrderedDict(),
                        timeout=None, retries=None, check_action_loop_detector=True, empty_loop_timeout=None,
                        **optional_args):

        """Get response form the device and compare it to action_map, error_map and expected_string patterns,
        perform actions specified in action_map if any, and return output.
        Raise Exception if receive empty responce from device within a minute

        :param command: command to send
        :param expected_string: expected string
        :param expect_map: dict with {re_str: action} to trigger some action on received string
        :param error_map: expected error list
        :param timeout: session timeout
        :param retries: maximal retries count
        :return:
        """
        if not command:
            command = ''

        retries = retries or self._max_loop_retries
        empty_loop_timeout = empty_loop_timeout or self._empty_loop_timeout

        if command is not None:
            self._clear_buffer(self._clear_buffer_timeout, logger)

            logger.debug('Command: {}'.format(command))
            self.send_line(command, logger)

        if expected_string is None or len(expected_string) == 0:
            raise Exception('ExpectSession', 'List of expected messages can\'t be empty!')

        # Loop until one of the expressions is matched or MAX_RETRIES
        # nothing is expected (usually used for exit)
        output_list = list()
        output_str = ''
        retries_count = 0
        is_correct_exit = False
        action_loop_detector = ActionLoopDetector(self._loop_detector_max_action_loops,
                                                  self._loop_detector_max_combination_length)

        while retries == 0 or retries_count < retries:

            try:
                read_buffer = self._receive(timeout, logger)
            except socket.timeout:
                read_buffer = None

            if read_buffer:
                output_str += read_buffer
                retries_count = 0
            else:
                retries_count += 1
                time.sleep(empty_loop_timeout)
                continue

            if re.search(expected_string, output_str, re.DOTALL):
                output_list.append(output_str)
                is_correct_exit = True

            for expect_string in action_map:
                result_match = re.search(expect_string, output_str, re.DOTALL)
                if result_match:
                    output_list.append(output_str)

                    if check_action_loop_detector:
                        if action_loop_detector.loops_detected(expect_string):
                            logger.error('Loops detected, output_list: {}'.format(''.join(output_list)))
                            raise SessionLoopDetectorException(self.__class__.__name__,
                                                               'Expected actions loops detected')
                    action_map[expect_string](self, logger)
                    output_str = ''
                    break

            if is_correct_exit:
                break

        if not is_correct_exit:
            raise SessionLoopLimitException(self.__class__.__name__,
                                            'Session Loop limit exceeded, {} loops'.format(retries_count))

        result_output = ''.join(output_list)

        for error_string in error_map:
            result_match = re.search(error_string, result_output, re.DOTALL)
            if result_match:
                logger.error(result_output)
                raise CommandExecutionException(self.__class__.__name__,
                                                'Session returned \'{}\''.format(error_map[error_string]))

        # Read buffer to the end. Useful when expected_string isn't last in buffer
        result_output += self._clear_buffer(self._clear_buffer_timeout, logger)

        result_output = normalize_buffer(result_output)
        logger.debug(result_output)
        return result_output

    def reconnect(self, prompt, logger):
        """
        Recconnect implementation

        :param prompt:
        :return:
        """
        self.disconnect()
        self.connect(prompt)

    def _default_actions(self, logger):
        """
        Call default action
        :return:
        """
        if self._default_actions_func:
            logger.debug('Calling default actions')
            self._default_actions_func(session=self, logger=logger)


class ActionLoopDetector(object):
    """Help to detect loops for action combinations"""

    def __init__(self, max_loops, max_combination_length):
        """

        :param max_loops:
        :param max_combination_length:
        :return:
        """
        self._max_action_loops = max_loops
        self._max_combination_length = max_combination_length
        self._action_history = []

    def loops_detected(self, action_key):
        """
        Add action key to the history and detect loops

        :param action_key:
        :return:
        """
        # """Added action key to the history and detect for loops"""
        loops_detected = False
        self._action_history.append(action_key)
        for combination_length in xrange(1, self._max_combination_length + 1):
            if self._is_combination_compatible(combination_length):
                if self._detect_loops_for_combination_length(combination_length):
                    loops_detected = True
                    break
        return loops_detected

    def _is_combination_compatible(self, combination_length):
        """
        Check if combinations may exist

        :param combination_length:
        :return:
        """
        if len(self._action_history) / combination_length >= self._max_action_loops:
            is_compatible = True
        else:
            is_compatible = False
        return is_compatible

    def _detect_loops_for_combination_length(self, combination_length):
        """
        Detect loops for combination length

        :param combination_length:
        :return:
        """
        reversed_history = self._action_history[::-1]
        combinations = [reversed_history[x:x + combination_length] for x in
                        xrange(0, len(reversed_history), combination_length)][:self._max_action_loops]
        is_loops_exist = True
        for x, y in [combinations[x:x + 2] for x in xrange(0, len(combinations) - 1)]:
            if x != y:
                is_loops_exist = False
                break
        return is_loops_exist
