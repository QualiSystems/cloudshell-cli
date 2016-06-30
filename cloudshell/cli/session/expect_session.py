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

    def __init__(self, handler=None, username=None, password=None, host=None, port=None,
                 timeout=60, new_line='\r', **kwargs):
        self.session_type = 'EXPECT'
        self._handler = handler
        self._port = port
        if host:
            temp_host = host.split(':')
            self._host = temp_host[0]
            if not self._port and len(temp_host) > 1:
                self._port = temp_host[1]
        else:
            self._host = host

        self._username = username
        self._password = password

        self._new_line = new_line
        self._timeout = timeout

        override_attributes_from_config(self)

        self._max_read_retries = self.HE_MAX_READ_RETRIES
        self._max_loop_retries = self.HE_MAX_LOOP_RETRIES
        self._empty_loop_timeout = self.HE_EMPTY_LOOP_TIMEOUT
        self._default_actions_func = self.DEFAULT_ACTIONS

    def _receive_with_retries(self, timeout, retries_count):
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
            except Exception as err:
                raise err
            break

        if current_output is None:
            raise Exception('ExpectSession', 'Failed to get response from device')
        return current_output

    def send_line(self, data_str):
        self._send(data_str + self._new_line)

    @inject.params(logger=LOGGER)
    def hardware_expect(self, data_str=None, re_string='', expect_map=OrderedDict(),
                        error_map=OrderedDict(), timeout=None, retries_count=None, logger=None):
        """Get response form the device and compare it to expected_map, error_map and re_string patterns,
        perform actions specified in expected_map if any, and return output.
        Will raise Exception if response from the device will be empty within a minute

        :param data_str:
        :param re_string:
        :param expect_map:
        :param error_map:
        :param timeout:
        :param retries_count:
        :return:
        """

        if retries_count is None:
            retries_count = self._max_loop_retries

        if data_str is not None:
            logger.debug(data_str)
            self.send_line(data_str)
            time.sleep(0.2)

        if re_string is None or len(re_string) == 0:
            raise Exception('ExpectSession', 'Expect list is empty!')


        # Loop until one of the expressions is matched or MAX_RETRIES
        # nothing is expected (usually used for exit)
        output_list = list()
        output_str = ''
        retries = 0
        is_correct_exit = False

        while retries_count == 0 or retries < retries_count:
            is_matched = False
            retries += 1
            output_str += self._receive_with_retries(timeout, self._max_read_retries)

            if re.search(re_string, output_str, re.DOTALL):
                output_list.append(output_str)
                is_correct_exit = True
                break

            for expect_string in expect_map:
                result_match = re.search(expect_string, output_str, re.DOTALL)
                if result_match:
                    expect_map[expect_string](self)
                    output_list.append(output_str)
                    output_str = ''
                    is_matched = True
                    break
            if not is_matched:
                time.sleep(self._empty_loop_timeout)

        if not is_correct_exit:
            raise Exception('ExpectSession', 'Loop limit exceeded')

        result_output = ''.join(output_list)

        for error_string in error_map:
            result_match = re.search(error_string, result_output, re.DOTALL)
            if result_match:
                logger.error(result_output)
                raise CommandExecutionException('ExpectSession', error_map[error_string])

        result_output = normalize_buffer(result_output)
        logger.debug(result_output)
        return result_output

    def reconnect(self, prompt):
        self.disconnect()
        self.connect(prompt)

    def _default_actions(self):
        if self._default_actions_func:
            self._default_actions_func(session=self)
