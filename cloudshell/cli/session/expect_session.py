import re
import time
from abc import ABCMeta, abstractmethod
from collections import OrderedDict

from cloudshell.cli.helper.normalize_buffer import normalize_buffer
from cloudshell.cli.session.session import Session
from cloudshell.cli.session.session_exceptions import SessionLoopDetectorException, SessionLoopLimitException, \
    ExpectedSessionException, CommandExecutionException, SessionReadTimeout, SessionReadEmptyData


class ExpectSession(Session):
    """
    Help to handle additional actions during send command
    """

    __metaclass__ = ABCMeta

    SESSION_TYPE = 'EXPECT'

    MAX_LOOP_RETRIES = 20
    READ_TIMEOUT = 30
    EMPTY_LOOP_TIMEOUT = 0.5
    CLEAR_BUFFER_TIMEOUT = 0.1
    LOOP_DETECTOR_MAX_ACTION_LOOPS = 3
    LOOP_DETECTOR_MAX_COMBINATION_LENGTH = 4
    RECONNECT_TIMEOUT = 30

    def __init__(self, timeout=READ_TIMEOUT, new_line='\r', max_loop_retries=MAX_LOOP_RETRIES,
                 empty_loop_timeout=EMPTY_LOOP_TIMEOUT, loop_detector_max_action_loops=LOOP_DETECTOR_MAX_ACTION_LOOPS,
                 loop_detector_max_combination_length=LOOP_DETECTOR_MAX_COMBINATION_LENGTH,
                 clear_buffer_timeout=CLEAR_BUFFER_TIMEOUT, reconnect_timeout=RECONNECT_TIMEOUT):

        """

        :param timeout:
        :param new_line:
        :param max_loop_retries:
        :param empty_loop_timeout:
        :param loop_detector_max_action_loops:
        :param loop_detector_max_combination_length:
        :param clear_buffer_timeout:
        :return:
        """

        self._new_line = new_line
        self._timeout = timeout
        self._max_loop_retries = max_loop_retries
        self._empty_loop_timeout = empty_loop_timeout

        self._loop_detector_max_action_loops = loop_detector_max_action_loops
        self._loop_detector_max_combination_length = loop_detector_max_combination_length
        self._clear_buffer_timeout = clear_buffer_timeout
        self._reconnect_timeout = reconnect_timeout

        self._active = False

    @property
    def session_type(self):
        return self.SESSION_TYPE

    @abstractmethod
    def _connect_actions(self, prompt, logger):
        """Read out buffer and run on_session_start actions
        :param prompt: expected string in output
        :param logger: logger
        """

        pass

    @abstractmethod
    def _initialize_session(self, prompt, logger):
        """Create handler and initialize session
        :param prompt: expected string in output
        :param logger: logger
        """
        pass

    def set_active(self, state):
        self._active = state

    def active(self):
        return self._active

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
            except (SessionReadTimeout, SessionReadEmptyData):
                read_buffer = None
            if read_buffer:
                out += read_buffer
            else:
                break
        return out

    def connect(self, prompt, logger):
        """Connect to device.
        :param prompt: expected string in output
        :param logger: logger
        """

        try:
            self._initialize_session(prompt, logger)
            self._connect_actions(prompt, logger)
            self.set_active(True)
        except:
            self.disconnect()
            raise

    def send_line(self, command, logger):
        """
        Add new line to the end of command string and send

        :param command:
        :return:
        """
        self._send(command + self._new_line, logger)

    def _receive_all(self, timeout, logger):
        """
        Read as much as possible before catch SessionTimeoutException
        :param timeout:
        :param logger:
        :return:
        :rtype: str
        """
        if not timeout:
            timeout = self._timeout
        start_time = time.time()
        read_buffer = ''
        while True:
            try:
                read_buffer += self._receive(0.1, logger)
            except (SessionReadTimeout, SessionReadEmptyData):
                if read_buffer:
                    return read_buffer
                elif time.time() - start_time > timeout:
                    raise ExpectedSessionException(self.__class__.__name__, 'Socket closed by timeout')

    def probe_for_prompt(self, expected_string, logger):
        return self.hardware_expect('', expected_string, logger)

    def hardware_expect(self, command, expected_string, logger, action_map=None, error_map=None,
                        timeout=None, retries=None, check_action_loop_detector=True, empty_loop_timeout=None,
                        remove_command_from_output=True, **optional_args):

        """Get response form the device and compare it to action_map, error_map and expected_string patterns,
        perform actions specified in action_map if any, and return output.
        Raise Exception if receive empty response from device within a minute

        :param command: command to send
        :param expected_string: expected string
        :param expect_map: dict with {re_str: action} to trigger some action on received string
        :param error_map: expected error list
        :param timeout: session timeout
        :param retries: maximal retries count
        :param remove_command_from_output: In some switches the output string includes the command which was called.
            The flag used to verify whether the the command string removed from the output string.
        :return:
        """

        if not action_map:
            action_map = OrderedDict()

        if not error_map:
            error_map = OrderedDict()

        retries = retries or self._max_loop_retries
        empty_loop_timeout = empty_loop_timeout or self._empty_loop_timeout

        if command is not None:
            self._clear_buffer(self._clear_buffer_timeout, logger)

            logger.debug('Command: {}'.format(command))
            self.send_line(command, logger)

        if not expected_string:
            raise ExpectedSessionException(self.__class__.__name__, 'List of expected messages can\'t be empty!')

        # Loop until one of the expressions is matched or MAX_RETRIES
        # nothing is expected (usually used for exit)
        output_list = list()
        output_str = ''
        retries_count = 0
        is_correct_exit = False

        action_loop_detector = ActionLoopDetector(self._loop_detector_max_action_loops,
                                                  self._loop_detector_max_combination_length)

        while retries == 0 or retries_count < retries:

            # try:
            # read_buffer = self._receive(timeout, logger)
            # read all data from buffer
            read_buffer = self._receive_all(timeout, logger)
            # except socket.timeout:
            #     read_buffer = None

            if read_buffer:
                read_buffer = normalize_buffer(read_buffer)
                logger.debug(read_buffer)
                output_str += read_buffer
                # if option remove_command_from_output is set to True, look for command in output buffer,
                #  remove it in case of found
                if command and remove_command_from_output:
                    command_pattern = '^.*' + command + '.*\\n'
                    if re.search(command_pattern, output_str):
                        output_str = re.sub(command_pattern, '', output_str)
                        remove_command_from_output = False
                retries_count = 0
            else:
                retries_count += 1
                time.sleep(empty_loop_timeout)
                continue

            if re.search(expected_string, output_str, re.DOTALL):
                # logger.debug('Expected str: {}'.format(expected_string))
                output_list.append(output_str)
                is_correct_exit = True

            for action_key in action_map:
                result_match = re.search(action_key, output_str, re.DOTALL)
                if result_match:
                    output_list.append(output_str)

                    if check_action_loop_detector:
                        if action_loop_detector.loops_detected(action_key):
                            logger.error('Loops detected')
                            raise SessionLoopDetectorException(self.__class__.__name__,
                                                               'Expected actions loops detected')
                    logger.debug('Action key: {}'.format(action_key))
                    action_map[action_key](self, logger)
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
                raise CommandExecutionException(self.__class__.__name__,
                                                'Session returned \'{}\''.format(error_map[error_string]))

        # Read buffer to the end. Useful when expected_string isn't last in buffer
        result_output += self._clear_buffer(self._clear_buffer_timeout, logger)
        return result_output

    def reconnect(self, prompt, logger, timeout=None):
        """
        Recconnect implementation

        :param prompt:
        :param logger:
        :param timeout:
        :return:
        """
        logger.debug('Reconnect')
        timeout = timeout or self._reconnect_timeout

        call_time = time.time()
        while time.time() - call_time < timeout:
            try:
                self.disconnect()
                return self.connect(prompt, logger)
            except Exception as e:
                logger.debug(e)
        raise ExpectedSessionException(self.__class__.__name__,
                                       'Reconnect unsuccessful, timeout exceeded, see logs for more details')


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
