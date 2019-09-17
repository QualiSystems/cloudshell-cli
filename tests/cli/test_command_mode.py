from unittest import TestCase

from cloudshell.cli.service.command_mode import CommandMode

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestCommandMode(TestCase):
    def setUp(self):
        self._prompt = Mock()
        self._enter_command = Mock()
        self._enter_action_map = Mock()
        self._enter_error_map = Mock()
        self._exit_command = Mock()
        self._exit_action_map = Mock()
        self._exit_error_map = Mock()
        self._enter_actions = Mock()
        self._session = Mock()
        self._command_mode = CommandMode(
            self._prompt,
            enter_command=self._enter_command,
            enter_action_map=self._enter_action_map,
            enter_error_map=self._enter_error_map,
            exit_command=self._exit_command,
            exit_action_map=self._exit_action_map,
            exit_error_map=self._exit_error_map,
            enter_actions=self._enter_actions,
            use_exact_prompt=False,
        )
        self._logger = Mock()

    def test_init(self):
        attributes = [
            "_enter_error_map",
            "_prompt",
            "_enter_command",
            "_exit_error_map",
            "_exit_command",
            "child_nodes",
            "_exit_action_map",
            "_enter_actions",
            "parent_node",
            "_enter_action_map",
            "_use_exact_prompt",
            "_exact_prompt",
        ]

        self.assertTrue(
            len(set(attributes).difference(set(self._command_mode.__dict__.keys())))
            == 0
        )

    def test_add_parent_mode(self):
        mode = Mock()
        self._command_mode.add_parent_mode(mode)
        mode.add_child_node.assert_called_once_with(self._command_mode)

    def test_step_up_send_command(self):
        cli_service = Mock()
        self._command_mode.step_up(cli_service, self._logger)
        cli_service.send_command.assert_called_once_with(
            self._enter_command,
            expected_string=self._prompt,
            action_map=self._enter_action_map,
            error_map=self._enter_error_map,
        )

    def test_step_up_set_command_mode(self):
        cli_service = Mock()
        self._command_mode.step_up(cli_service, self._logger)
        self.assertTrue(cli_service.command_mode == self._command_mode)

    def test_step_up_call_enter_actions(self):
        cli_service = Mock()
        enter_actions = Mock()
        self._command_mode.enter_actions = enter_actions
        self._command_mode.step_up(cli_service, self._logger)
        enter_actions.assert_called_once_with(cli_service)

    def test_step_down_sent_command(self):
        cli_service = Mock()
        parent_prompt = Mock()
        parent_node = Mock()
        parent_node.prompt = parent_prompt
        self._command_mode.parent_node = parent_node
        self._command_mode.step_down(cli_service, self._logger)
        cli_service.send_command.assert_called_once_with(
            self._exit_command,
            expected_string=parent_prompt,
            action_map=self._exit_action_map,
            error_map=self._exit_error_map,
        )

    def test_step_down_set_mode(self):
        cli_service = Mock()
        parent_prompt = Mock()
        parent_node = Mock()
        parent_node.prompt = parent_prompt
        self._command_mode.parent_node = parent_node
        self._command_mode.step_down(cli_service, self._logger)
        self.assertTrue(cli_service.command_mode == parent_node)

    def test_get_all_attached_command_mode(self):
        class CommandModeA(CommandMode):
            pass

        class CommandModeB(CommandMode):
            pass

        CommandMode.RELATIONS_DICT = {CommandModeA: {CommandModeB: {}}}

        command_modes = list(CommandMode.get_all_attached_command_modes())

        self.assertEqual(command_modes, [CommandModeA, CommandModeB])

    def test_is_attached_command_mode(self):
        class CommandModeA(CommandMode):
            pass

        class CommandModeB(CommandMode):
            pass

        CommandMode.RELATIONS_DICT = {CommandModeA: {}}

        command_mode_a = CommandModeA("")
        command_mode_b = CommandModeB("")

        self.assertTrue(command_mode_a.is_attached_command_mode())
        self.assertFalse(command_mode_b.is_attached_command_mode())
