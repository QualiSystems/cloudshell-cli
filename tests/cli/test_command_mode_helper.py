from unittest import TestCase

from cloudshell.cli.service.command_mode import CommandModeException
from cloudshell.cli.service.command_mode_helper import CommandModeHelper

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestCommandModeHelper(TestCase):
    def setUp(self):
        self._session = Mock()
        self._command_mode = Mock()
        self._logger = Mock()

    @patch(
        "cloudshell.cli.service.command_mode_helper.CommandModeHelper"
        ".defined_modes_by_prompt"
    )
    def test_determine_current_mode_call_defined_modes(self, defined_modes_by_prompt):
        prompt = "test"
        defined_modes_by_prompt.return_value = {prompt: self._command_mode}
        self._session.probe_for_prompt.return_value = prompt
        CommandModeHelper.determine_current_mode(
            self._session, self._command_mode, self._logger
        )
        defined_modes_by_prompt.assert_called_once_with(self._command_mode)

    @patch(
        "cloudshell.cli.service.command_mode_helper.CommandModeHelper"
        ".defined_modes_by_prompt"
    )
    def test_determine_current_mode_call_probe_for_prompt(
        self, defined_modes_by_prompt
    ):
        prompt = "test"
        defined_modes = {prompt: self._command_mode}
        defined_modes_by_prompt.return_value = defined_modes
        self._session.probe_for_prompt.return_value = prompt
        CommandModeHelper.determine_current_mode(
            self._session, self._command_mode, self._logger
        )
        prompts_re = r"|".join(defined_modes.keys())
        self._session.probe_for_prompt.assert_called_once_with(
            expected_string=prompts_re, logger=self._logger
        )

    @patch(
        "cloudshell.cli.service.command_mode_helper.CommandModeHelper"
        ".defined_modes_by_prompt"
    )
    def test_determine_current_mode_raise_exception(self, defined_modes_by_prompt):
        prompt = "test"
        defined_modes_by_prompt.return_value = {prompt: self._command_mode}
        self._session.probe_for_prompt = Mock(side_effect=Exception())
        exception = CommandModeException
        with self.assertRaises(exception):
            CommandModeHelper.determine_current_mode(
                self._session, self._command_mode, self._logger
            )

    @patch(
        "cloudshell.cli.service.command_mode_helper.CommandModeHelper"
        ".defined_modes_by_prompt"
    )
    def test_determine_current_mode_return_mode(self, defined_modes_by_prompt):
        prompt = "test"
        defined_modes_by_prompt.return_value = {prompt: self._command_mode}
        self._session.probe_for_prompt.return_value = prompt
        mode = CommandModeHelper.determine_current_mode(
            self._session, self._command_mode, self._logger
        )
        self.assertTrue(mode == self._command_mode)
