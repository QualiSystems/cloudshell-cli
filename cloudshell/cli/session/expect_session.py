import socket
import time
from collections import OrderedDict

from abc import ABCMeta
import re
from cloudshell.cli.session.session import Session
from cloudshell.cli.helper.normalize_buffer import normalize_buffer
from cloudshell.cli.service.cli_exceptions import CommandExecutionException
import inject
from cloudshell.configuration.cloudshell_shell_core_binding_keys import LOGGER
from cloudshell.shell.core.config_utils import override_attributes_from_config


class ExpectSession(Session):
    __metaclass__ = ABCMeta

    DEFAULT_ACTIONS = None
    HE_MAX_LOOP_RETRIES = 100
    HE_MAX_READ_RETRIES = 5
    HE_EMPTY_LOOP_TIMEOUT = 0.2
    HE_LOOP_DETECTOR_MAX_ACTION_LOOPS = 3
    HE_LOOP_DETECTOR_MAX_COMBINATION_LENGTH = 4

    def __init__(self, handler=None, username=None, password=None, host=None, port=None,
                 timeout=60, new_line='\r', **kwargs):
        self.session_type = 'EXPECT'
        self._handler = handler
        self._port = port
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

        """Override constants with global config values"""
        overridden_config = override_attributes_from_config(ExpectSession)

        self._max_read_retries = overridden_config.HE_MAX_READ_RETRIES
        self._max_loop_retries = overridden_config.HE_MAX_LOOP_RETRIES
        self._empty_loop_timeout = overridden_config.HE_EMPTY_LOOP_TIMEOUT
        self._default_actions_func = overridden_config.DEFAULT_ACTIONS
        self._loop_detector_max_action_loops = overridden_config.HE_LOOP_DETECTOR_MAX_ACTION_LOOPS
        self._loop_detector_max_combination_length = overridden_config.HE_LOOP_DETECTOR_MAX_COMBINATION_LENGTH

    @property
    def logger(self):
        return inject.instance(LOGGER)

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

    def send_line(self, data_str):
        self._send(data_str + self._new_line)

    def hardware_expect(self, data_str=None, re_string='', expect_map=OrderedDict(), error_map=OrderedDict(),
                        timeout=None, retries=None, check_action_loop_detector=True, **optional_args):

        """Get response form the device and compare it to expected_map, error_map and re_string patterns,
        perform actions specified in expected_map if any, and return output.
        Raise Exception if receive empty responce from device within a minute

        :param data_str: command to send
        :param re_string: expected string
        :param expect_map: dict with {re_str: action} to trigger some action on received string
        :param error_map: expected error list
        :param timeout: session timeout
        :param retries: maximal retries count
        :return:
        """

        if retries is None:
            retries = self._max_loop_retries

        if data_str is not None:
            try:
                # Try to read buffer before sending command. Workaround for clear buffer
                output_str = self._receive_with_retries(1, 1)
            except:
                pass

            self.logger.debug(data_str)
            self.send_line(data_str)
            time.sleep(0.2)

        if re_string is None or len(re_string) == 0:
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
            is_matched = False
            retries_count += 1
            output_str += self._receive_with_retries(timeout, self._max_read_retries)

            if re.search(re_string, output_str, re.DOTALL):
                output_list.append(output_str)
                is_correct_exit = True

            for expect_string in expect_map:
                result_match = re.search(expect_string, output_str, re.DOTALL)
                if result_match:
                    output_list.append(output_str)

                    if check_action_loop_detector:
                        if not action_loop_detector.check_loops(expect_string):
                            self.logger.error('Loops detected, output_list: {}'.format(output_list))
                            raise Exception('hardware_expect', 'Expected actions loops detected')
                    expect_map[expect_string](self)
                    output_str = ''
                    is_matched = True
                    break

            if is_correct_exit:
                break

            if not is_matched:
                time.sleep(self._empty_loop_timeout)

        if not is_correct_exit:
            raise Exception('ExpectSession', 'Session Loop limit exceeded, {} loops'.format(retries_count))

        result_output = ''.join(output_list)

        for error_string in error_map:
            result_match = re.search(error_string, result_output, re.DOTALL)
            if result_match:
                self.logger.error(result_output)
                raise CommandExecutionException('ExpectSession',
                                                'Session returned \'{}\''.format(error_map[error_string]))
        try:
            # Read buffer to the end. Useful when re_string isn't last in buffer
            output_str = self._receive_with_retries(1, 1)
            result_output += output_str
        except:
            pass

        result_output = normalize_buffer(result_output)
        self.logger.debug(result_output)
        return result_output

    def reconnect(self, prompt):
        self.disconnect()
        self.connect(prompt)

    def _default_actions(self):
        if self._default_actions_func:
            self._default_actions_func(session=self)


class ActionLoopDetector(object):
    """Class which helps to detect loops for action combinations"""

    def __init__(self, max_loops, max_combination_length):
        self._max_action_loops = max_loops
        self._max_combination_length = max_combination_length
        self._action_history = []

    @property
    def logger(self):
        return inject.instance(LOGGER)

    @property
    def action_history_len(self):
        return len(self._action_history)

    def check_loops(self, action_key):
        """Add action in history, look for loops in action history"""
        is_correct = True

        self._action_history.append(action_key)
        for index in reversed(range(0, len(self._action_history))):
            if not self._check_loop_for_index(index):
                is_correct = False
                self.logger.error('Action history: {}'.format(self._action_history))
                break
        return is_correct

    def _check_loop_for_index(self, index):
        """Check if index of history can have loops then check for loops"""
        is_different = True
        combination_len = self.action_history_len - index
        if combination_len <= self._max_combination_length:
            """Check if combination length is suitable"""
            if self.action_history_len / (self.action_history_len - index) >= self._max_action_loops:
                combinations = []
                """Check if combinations count can be in the history"""
                for combination_index in range(self._max_action_loops):
                    index_start = (self.action_history_len - 1) - (combination_len * combination_index) - (
                        combination_len - 1)
                    """get start index for combination"""
                    index_end = (self.action_history_len - 1) - (combination_len * combination_index)
                    """get end index for combination"""
                    combinations.append(self._get_combination(index_start, index_end))
                is_different = self._are_combinations_different(combinations)
        return is_different

    def _get_combination(self, index_start, index_end):
        """create combination from history by indexes"""
        combination = []
        for index in range(index_start, index_end + 1):
            combination.append(self._action_history[index])
        return combination

    def _are_combinations_different(self, combinations):
        """check if combinations are different"""
        is_different = False
        previous_combination = combinations.pop(0)
        for combination in combinations:
            if combination != previous_combination:
                is_different = True
                break
            else:
                previous_combination = combination

        return is_different
