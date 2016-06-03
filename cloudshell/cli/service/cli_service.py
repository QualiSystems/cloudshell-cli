import time

from cloudshell.cli.service.cli_service_interface import CliServiceInterface
from cloudshell.cli.service.cli_exceptions import CommandExecutionException
from cloudshell.shell.core.config_utils import get_config_attribute_or_none
import cloudshell.configuration.cloudshell_cli_configuration as package_config
from cloudshell.configuration.cloudshell_cli_binding_keys import SESSION
from cloudshell.configuration.cloudshell_shell_core_binding_keys import CONFIG, LOGGER
import re
import inject


class CliService(CliServiceInterface):
    @inject.params(config=CONFIG)
    def __init__(self, config):
        if not config:
            raise Exception(self.__class__.__name__, 'Config not defined')
        self._config = config
        self._expected_map = get_config_attribute_or_none('EXPECTED_MAP', self._config) or package_config.EXPECTED_MAP
        self._error_map = get_config_attribute_or_none('ERROR_MAP', self._config) or package_config.ERROR_MAP
        self._command_retries = get_config_attribute_or_none('COMMAND_RETRIES',
                                                             self._config) or package_config.COMMAND_RETRIES
        self._prompt = get_config_attribute_or_none('DEFAULT_PROMPT', self._config) or package_config.DEFAULT_PROMPT
        self._config_mode_prompt = get_config_attribute_or_none('CONFIG_MODE_PROMPT',
                                                                self._config) or package_config.CONFIG_MODE_PROMPT
        self._enter_config_mode_prompt_command = get_config_attribute_or_none('ENTER_CONFIG_MODE_PROMPT_COMMAND',
                                                                              self._config) or package_config.ENTER_CONFIG_MODE_PROMPT_COMMAND
        self._exit_config_mode_prompt_command = get_config_attribute_or_none('EXIT_CONFIG_MODE_PROMPT_COMMAND',
                                                                             self._config) or package_config.EXIT_CONFIG_MODE_PROMPT_COMMAND

    @inject.params(logger=LOGGER, session=SESSION)
    def send_config_command(self, command, expected_str=None, expected_map=None, timeout=30, retries=10,
                            is_need_default_prompt=False, logger=None, session=None):
        """Send command into configuration mode, enter to config mode if needed

        :param command: command to send
        :param expected_str: expected output string (_prompt by default)
        :param timeout: command timeout
        :return: received output buffer
        """

        self._enter_configuration_mode(session)

        if expected_str is None:
            expected_str = self._prompt

        out = self._send_command(command, expected_str, expected_map=expected_map, retries=retries,
                                 is_need_default_prompt=is_need_default_prompt, timeout=timeout, session=session)
        logger.info(out)
        return out

    @inject.params(logger=LOGGER, session=SESSION)
    def send_command(self, command, expected_str=None, expected_map=None, timeout=30, retries=10,
                     is_need_default_prompt=True, logger=None, session=None):
        """Send command in default mode

        :param command: command to send
        :param expected_str: expected output string (_prompt by default)
        :param expected_map: action map (string - action)
        :param timeout: command timeout
        :param retries: retries to send command
        :param is_need_default_prompt:
        :param logger:
        :param session:
        :return: received output buffer
        """

        self.exit_configuration_mode(session)
        try:
            out = self._send_command(command, expected_str, expected_map=expected_map, retries=retries,
                                     is_need_default_prompt=is_need_default_prompt, timeout=timeout, session=session)
        except CommandExecutionException as e:
            self.rollback()
            logger.error(e)
            raise e
        return out

    @inject.params(logger=LOGGER)
    def _send_command(self, command, expected_str=None, expected_map=None, timeout=30, retries=10,
                      is_need_default_prompt=True, logger=None, session=None):

        """Send command
        :param command: command to send
        :param expected_str: expected output string (_prompt by default)
        :param timeout: command timeout
        :return: received output buffer
        """

        if not expected_map:
            expected_map = self._expected_map

        if not expected_str:
            expected_str = self._prompt
        else:
            if is_need_default_prompt:
                expected_str = expected_str + '|' + self._prompt

        out = ''
        for retry in range(self._command_retries):
            try:
                out = session.hardware_expect(command, expected_str, expect_map=expected_map,
                                              error_map=self._error_map, retries_count=retries,
                                              timeout=timeout)
                break
            except Exception as e:
                logger.error(e)
                if retry == self._command_retries - 1:
                    raise Exception('Can not send command')
                session.reconnect(self._prompt)
        return out

    def send_command_list(self, commands_list, send_command_func=None):
        output = ""
        if not send_command_func:
            send_command_func = self.send_config_command
        for command in commands_list:
            output += send_command_func(command)
        return output

    @inject.params(logger=LOGGER, session=SESSION)
    def exit_configuration_mode(self, session=None, logger=None):
        """Send 'enter' to SSH console to get prompt,
        if config prompt received , send 'exit' command, change _prompt to DEFAULT
        else: return
        :return: console output
        """

        out = None
        for retry in range(5):
            out = self._send_command(' ', session=session)
            if re.search(self._config_mode_prompt, out):
                self._send_command(self._exit_config_mode_prompt_command, session=session)
            else:
                break

        return out

    @inject.params(logger=LOGGER)
    def _enter_configuration_mode(self, session=None, logger=None):
        """Send 'enter' to SSH console to get prompt,
        if default prompt received , send 'configure terminal' command, change _prompt to CONFIG_MODE
        else: return

        :return: True if config mode entered, else - False
        """

        out = None
        for retry in range(3):
            out = self._send_command(' ', session=session)
            if not out:
                logger.error('Failed to get prompt, retrying ...')
                time.sleep(1)

            elif not re.search(self._config_mode_prompt, out):
                out = self._send_command(self._enter_config_mode_prompt_command, self._config_mode_prompt,
                                         session=session)

            else:
                break

        if not out:
            return False
        # self._prompt = self.CONFIG_MODE_PROMPT
        return re.search(self._prompt, out)

    def rollback(self):
        pass
