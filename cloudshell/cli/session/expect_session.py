__author__ = 'g8y3e'

import socket
import time
from collections import OrderedDict

from abc import ABCMeta
import re
from cloudshell.cli.session.session import Session
from cloudshell.cli.helper.normalize_buffer import normalize_buffer
from cloudshell.cli.service.cli_exceptions import CommandExecutionException
import inject
from cloudshell.configuration.cloudshell_shell_core_binding_keys import LOGGER, CONFIG


class ExpectSession(Session):
    __metaclass__ = ABCMeta

    def __init__(self, handler=None, username=None, password=None, host=None, port=None,
                 timeout=60, new_line='\r', **kwargs):
        self._handler = handler
        self._host = host
        self._port = port
        self._username = username
        self._password = password

        self._new_line = new_line
        self._timeout = timeout
        self._default_actions_func = None
        if inject.is_configured():
            self._config = inject.instance(CONFIG)
            if hasattr(self._config, 'DEFAULT_ACTIONS'):
                self._default_actions_func = self._config.DEFAULT_ACTIONS

    def _receive_with_retries(self, timeout, retries_count):
        current_retries = 0
        current_output = None

        while current_retries < retries_count:
            current_retries += 1

            try:
                current_output = self._receive(timeout)
            except socket.timeout:
                continue
            except Exception as err:
                raise err

            break

        return current_output

    def send_line(self, data_str):
        self._send(data_str + self._new_line)

    @inject.params(logger=LOGGER)
    def hardware_expect(self, data_str=None, re_string='', expect_map=OrderedDict(),
                        error_map=OrderedDict(), timeout=None, retries_count=3, logger=None):
        """

        :param data_str:
        :param re_string:
        :param expect_map:
        :param error_map:
        :param timeout:
        :param retries_count:
        :return:
        """

        if data_str is not None:
            logger.info('Send command: ' + data_str)
            self.send_line(data_str)

        if re_string is None or len(re_string) == 0:
            raise Exception('ExpectSession', 'Expect list is empty!')

        output_str = self._receive_with_retries(timeout, retries_count)
        if output_str is None:
            raise Exception('ExpectSession', 'Empty response from device!')

        # Loop until one of the expressions is matched or loop forever if
        # nothing is expected (usually used for exit)
        output_list = list()
        while True:
            if re.search(re_string, output_str, re.DOTALL):
                logger.info('Output is:\n{0}'.format(output_str))
                break
            else:
                time.sleep(0.2)

            for expect_string in expect_map:
                result_match = re.search(expect_string, output_str, re.DOTALL)
                if result_match:
                    expect_map[expect_string](self)
                    output_list.append(output_str)
                    output_str = ''

            current_output = self._receive_with_retries(timeout, retries_count)
            if current_output is None:
                output_str = ''.join(output_list) + output_str
                logger.error("Can't find prompt in output: \n" + output_str)
                raise Exception('ExpectSession', 'Empty response from device!')
            output_str += current_output

        output_str = ''.join(output_list) + output_str
        for error_string in error_map:
            result_match = re.search(error_string, output_str, re.DOTALL)
            if result_match:
                raise CommandExecutionException('ExpectSession', error_map[error_string])

        return normalize_buffer(output_str)

    def reconnect(self, prompt):
        self.disconnect()
        self.connect(prompt)

    def _default_actions(self):
        if self._default_actions_func:
            self._default_actions_func(session=self)
