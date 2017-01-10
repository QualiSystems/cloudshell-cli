from unittest import TestCase
from cloudshell.cli.cli_service_impl import CommandModeContextManager, CliServiceImpl
from mock import Mock, patch


class TestCommandModeContextManager(TestCase):
    def setUp(self):
        self._cli_service = Mock()
        self._command_mode = Mock()
        self._logger = Mock()
        self._instance = CommandModeContextManager(self._cli_service, self._command_mode, self._logger)

    def test_init(self):
        mandatory_attributes = ['_logger', '_previous_mode', '_cli_service', '_command_mode']
        self.assertEqual(len(set(mandatory_attributes).difference(set(self._instance.__dict__.keys()))), 0)

    def test_enter_call_step_up(self):
        operations = self._instance.__enter__()
        self._command_mode.step_up.assert_called_once_with(self._cli_service)
        self.assertEqual(operations, self._cli_service)

    def test_enter_call_step_down(self):
        self._instance.__exit__(Mock(), Mock(), Mock())
        self._command_mode.step_down.assert_called_once_with(self._cli_service)


class TestCliOperationsImpl(TestCase):
    def setUp(self):
        self._session = Mock()
        self._command_mode = Mock()
        self._logger = Mock()
        self._determine_current_mode_func = None
        self._determined_command_mode = Mock()
        self._change_mode_func = None
        self._instance = self._create_instance()

    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.determine_current_mode')
    @patch('cloudshell.cli.cli_service_impl.CliServiceImpl._change_mode')
    def _create_instance(self, change_mode, determine_current_mode):
        self._determine_current_mode_func = determine_current_mode
        self._determine_current_mode_func.return_value = self._determined_command_mode
        self._change_mode_func = change_mode
        return CliServiceImpl(self._session, self._command_mode, self._logger)

    def test_init_attributes(self):
        mandatory_attributes = ['_logger', 'session', 'command_mode']
        self.assertEqual(len(set(mandatory_attributes).difference(set(self._instance.__dict__.keys()))), 0)

    def test_init_determine_current_mode_call(self):
        self._determine_current_mode_func.assert_called_once_with(self._session, self._command_mode, self._logger)

    def test_init_determined_mode_enter_actions_call(self):
        self._determined_command_mode.enter_actions.assert_called_once_with(self._instance)

    def test_init_change_mod_call(self):
        self._change_mode_func.assert_called_once_with(self._command_mode)

    @patch("cloudshell.cli.cli_service_impl.CommandModeContextManager")
    def test_enter_mode(self, command_mode_context_manager):
        command_mode_context_manager_instance = Mock()
        command_mode_context_manager.return_value = command_mode_context_manager_instance
        command_mode = Mock()
        instance = self._instance.enter_mode(command_mode)
        command_mode_context_manager.assert_called_once_with(self._instance, command_mode, self._logger)
        self.assertEqual(command_mode_context_manager_instance, instance)

    def test_send_command_hardware_expect_call(self):
        command = Mock()
        expected_string = Mock()
        self._instance.send_command(command, expected_string=expected_string, logger=self._logger)
        self._session.hardware_expect.assert_called_once_with(command, action_map=None, error_map=None,
                                                              expected_string=expected_string, logger=self._logger)

    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.calculate_route_steps')
    def test_change_mode_calculate_steps(self, calculate_route_steps):
        command_mode = Mock()
        self._instance._change_mode(command_mode)
        calculate_route_steps.assert_called_once_with(self._determined_command_mode, command_mode)

    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.defined_modes_by_prompt')
    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.determine_current_mode')
    @patch('cloudshell.cli.cli_service_impl.CliServiceImpl._change_mode')
    def test_reconnect_get_prompts(self, change_mode, determine_current_mode, defined_modes_by_prompt):
        prompt = 'test'
        command_mode = Mock()
        defined_modes_by_prompt.return_value = {prompt: command_mode}
        self._instance.reconnect()
        defined_modes_by_prompt.assert_called_once_with(self._determined_command_mode)

    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.defined_modes_by_prompt')
    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.determine_current_mode')
    @patch('cloudshell.cli.cli_service_impl.CliServiceImpl._change_mode')
    def test_reconnect_session_call(self, change_mode, determine_current_mode, defined_modes_by_prompt):
        prompt = 'test'
        command_mode = Mock()
        timeout = Mock()
        defined_modes_by_prompt.return_value = {prompt: command_mode}
        self._instance.reconnect(timeout)
        self._session.reconnect.assert_called_once_with(prompt, self._logger, timeout)

    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.defined_modes_by_prompt')
    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.determine_current_mode')
    @patch('cloudshell.cli.cli_service_impl.CliServiceImpl._change_mode')
    def test_reconnect_determine_current_mode_call(self, change_mode, determine_current_mode, defined_modes_by_prompt):
        prompt = 'test'
        command_mode = Mock()
        timeout = Mock()
        defined_modes_by_prompt.return_value = {prompt: command_mode}
        determine_current_mode.return_value = command_mode
        self._instance.reconnect(timeout)
        determine_current_mode.assert_called_once_with(self._session, self._determined_command_mode, self._logger)

    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.defined_modes_by_prompt')
    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.determine_current_mode')
    @patch('cloudshell.cli.cli_service_impl.CliServiceImpl._change_mode')
    def test_reconnect_command_mode_enter_action_call(self, change_mode, determine_current_mode,
                                                      defined_modes_by_prompt):
        prompt = 'test'
        command_mode = Mock()
        timeout = Mock()
        defined_modes_by_prompt.return_value = {prompt: command_mode}
        determine_current_mode.return_value = command_mode
        self._instance.reconnect(timeout)
        command_mode.enter_actions.assert_called_once_with(self._instance)

    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.defined_modes_by_prompt')
    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.determine_current_mode')
    @patch('cloudshell.cli.cli_service_impl.CliServiceImpl._change_mode')
    def test_reconnect_change_mode(self, change_mode, determine_current_mode,
                                   defined_modes_by_prompt):
        prompt = 'test'
        command_mode = Mock()
        timeout = Mock()
        defined_modes_by_prompt.return_value = {prompt: command_mode}
        determine_current_mode.return_value = command_mode
        self._instance.reconnect(timeout)
        change_mode.assert_called_once_with(self._determined_command_mode)
