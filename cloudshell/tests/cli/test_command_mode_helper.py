from unittest import TestCase
from cloudshell.cli.command_mode import CommandModeException
from cloudshell.cli.command_mode_helper import CommandModeHelper
from mock import Mock, patch


class TestCommandModeHelper(TestCase):
    def setUp(self):
        self._session = Mock()
        self._command_mode = Mock()
        self._logger = Mock()

    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.defined_modes_by_prompt')
    def test_determine_current_mode_call_defined_modes(self, defined_modes_by_prompt):
        prompt = 'test'
        defined_modes_by_prompt.return_value = {prompt: self._command_mode}
        self._session.hardware_expect.return_value = prompt
        mode = CommandModeHelper.determine_current_mode(self._session, self._command_mode, self._logger)
        defined_modes_by_prompt.assert_called_once_with(self._command_mode)

    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.defined_modes_by_prompt')
    def test_determine_current_mode_call_hardware_expect(self, defined_modes_by_prompt):
        prompt = 'test'
        defined_modes_by_prompt.return_value = {prompt: self._command_mode}
        self._session.hardware_expect.return_value = prompt
        mode = CommandModeHelper.determine_current_mode(self._session, self._command_mode, self._logger)
        self._session.hardware_expect.assert_called_once_with('', expected_string=prompt, logger=self._logger)

    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.defined_modes_by_prompt')
    def test_determine_current_mode_raise_exception(self, defined_modes_by_prompt):
        prompt = 'test'
        defined_modes_by_prompt.return_value = {prompt: self._command_mode}
        self._session.hardware_expect = Mock(side_effect=Exception())
        exception = CommandModeException
        with self.assertRaises(exception):
            mode = CommandModeHelper.determine_current_mode(self._session, self._command_mode, self._logger)

    @patch('cloudshell.cli.command_mode_helper.CommandModeHelper.defined_modes_by_prompt')
    def test_determine_current_mode_return_mode(self, defined_modes_by_prompt):
        prompt = 'test'
        defined_modes_by_prompt.return_value = {prompt: self._command_mode}
        self._session.hardware_expect.return_value = prompt
        mode = CommandModeHelper.determine_current_mode(self._session, self._command_mode, self._logger)
        self.assertTrue(mode == self._command_mode)
