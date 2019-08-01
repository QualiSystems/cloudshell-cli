import re
import time

from cloudshell.cli.service.action_map import ActionMap
from cloudshell.cli.service.error_map import ErrorMap
from cloudshell.cli.service.action_map import ActionLoopDetector
from cloudshell.cli.session.helper.normalize_buffer import normalize_buffer
from cloudshell.cli.session.session_exceptions import SessionLoopLimitException, ExpectedSessionException, \
    CommandExecutionException, SessionReadTimeout, SessionReadEmptyData

# option 1: save state in Command object
# option 2: save state ib this class


class CommandRunner:
    def __init__(self, session):
        self._session = session

    def _send_command(self, command):
        self.session._clear_buffer(self._clear_buffer_timeout, logger)
        logger.debug(f'Command: {command}')
        self.send_line(command, logger)

    def _remove_command_from_output(self, command, output):
        """If option remove_command_from_output is set to True, look for command in output buffer,

        remove it in case of found
        :param command:
        :return:
        """
        command_pattern = self._generate_command_pattern(command.command)
        if re.search(command_pattern, output, flags=re.MULTILINE):
            output = re.sub(command_pattern, '', output, count=1, flags=re.MULTILINE)
            command.remove_command_from_output = False

        return output

    def _wait_for_response(self):
        pass

    def hardware_expect(self, command, logger):
        """Get response form the device and compare it to action_map, error_map and expected_string patterns,

        perform actions specified in action_map if any, and return output.
        Raise Exception if receive empty response from device within a minute
        """
        if command.command:
            self._send_command(command.command)

        # Loop until one of the expressions is matched or MAX_RETRIES
        # nothing is expected (usually used for exit)
        output_list = list()
        output_str = ''
        retries_count = 0
        is_correct_exit = False

        while command.retries == 0 or retries_count < command.retries:
            read_buffer = self._session._receive_all(command.timeout, logger)

            if read_buffer:
                read_buffer = normalize_buffer(read_buffer)
                logger.debug(read_buffer)
                output_str += read_buffer

                if command.command and command.remove_command_from_output:
                    output_str = self._remove_command_from_output(output_str, command)

                retries_count = 0
            else:
                retries_count += 1
                time.sleep(command.empty_loop_timeout)
                continue

            if self.session.match_prompt(command.expected_string, output_str, logger):
                # logger.debug('Expected str: {}'.format(expected_string))
                output_list.append(output_str)
                is_correct_exit = True

            action_matched = command.action_map.process(session=self,
                                                        logger=logger,
                                                        output=output_str,
                                                        check_action_loop_detector=command.check_action_loop_detector,
                                                        action_loop_detector=command.action_loop_detector)

            if action_matched:
                output_list.append(output_str)
                output_str = ''

            if is_correct_exit:
                break

        if not is_correct_exit:
            raise SessionLoopLimitException(f'Session Loop limit exceeded, {retries_count} loops')

        result_output = ''.join(output_list)
        command.error_map.process(output=result_output, logger=logger)

        # Read buffer to the end. Useful when expected_string isn't last in buffer
        result_output += self._clear_buffer(self._clear_buffer_timeout, logger)
        return result_output


class Command:
    MAX_LOOP_RETRIES = 20
    READ_TIMEOUT = 30
    EMPTY_LOOP_TIMEOUT = 0.5
    CLEAR_BUFFER_TIMEOUT = 0.1
    LOOP_DETECTOR_MAX_ACTION_LOOPS = 3
    LOOP_DETECTOR_MAX_COMBINATION_LENGTH = 4
    RECONNECT_TIMEOUT = 30

    def __init__(self, command, expected_string, action_map=None, error_map=None,
                 timeout=None, retries=MAX_LOOP_RETRIES, check_action_loop_detector=True, empty_loop_timeout=None,
                 remove_command_from_output=True):
        """

        :param str command: command to send
        :param str expected_string: expected string
        :param collections.OrderedDict action_map: dict with {re_str: action} to trigger some action on received string
        :param error_map: expected error map with subclass of CommandExecutionException or str
        :type error_map: dict[str, CommandExecutionException|str]
        :param int timeout: session timeout
        :param int retries: maximal retries count
        :param bool check_action_loop_detector:
        :param bool empty_loop_timeout:
        :param bool remove_command_from_output: In some switches the output string includes the command which was called.
            The flag used to verify whether the the command string removed from the output string.
        :rtype: str
        """
        self.command = command
        self.expected_string = expected_string
        self.action_map = action_map or ActionMap()
        self.error_map = error_map or ErrorMap()

        if check_action_loop_detector:
            self.action_loop_detector = ActionLoopDetector(
                max_loops=self._loop_detector_max_action_loops,
                max_combination_length=self._loop_detector_max_combination_length)
        else:
            self.action_loop_detector = None
