from unittest import TestCase

from cloudshell.cli.service.session_pool_context_manager import (
    SessionPoolContextManager,
)
from cloudshell.cli.session.session_exceptions import CommandExecutionException

try:
    from unittest.mock import MagicMock as Mock
    from unittest.mock import call, patch
except ImportError:
    from mock import MagicMock as Mock
    from mock import call, patch


class TestSessionPoolContextManager(TestCase):
    def setUp(self):
        self._session_pool_manager = Mock()
        self._logger = Mock()
        self._new_sessions = Mock()
        self._connection_attrs = Mock()
        self._command_mode = Mock()
        self._instance = SessionPoolContextManager(
            self._session_pool_manager,
            self._new_sessions,
            self._command_mode,
            self._logger,
        )

    @patch("cloudshell.cli.service.session_pool_context_manager.CliService")
    def test_initialize_cli_service(self, cli_service_class):
        session = Mock()
        prompt = Mock()
        self._instance._initialize_cli_service(session, prompt)
        cli_service_class.assert_called_once_with(
            session, self._command_mode, self._logger
        )

    @patch("cloudshell.cli.service.session_pool_context_manager.CliService")
    def test_initialize_cli_service_call_reconnect(self, cli_service_class):
        session = Mock()
        prompt = Mock()
        cli_service = Mock()
        cli_service_class.side_effect = [Exception(), cli_service]
        self.assertIs(
            self._instance._initialize_cli_service(session, prompt), cli_service
        )
        cli_service_calls = [call(session, self._command_mode, self._logger)] * 2
        cli_service_class.assert_has_calls(cli_service_calls)
        session.reconnect.assert_called_once_with(prompt, self._logger)

    @patch("cloudshell.cli.service.session_pool_context_manager.CommandModeHelper")
    def test_enter_without_exception(self, command_mode_helper):
        self._instance._initialize_cli_service = Mock()
        prompts = ["1"]
        command_mode_helper.defined_modes_by_prompt.return_value = Mock()
        command_mode_helper.defined_modes_by_prompt.return_value.keys.return_value = (
            prompts
        )
        session = Mock()
        self._session_pool_manager.get_session.return_value = session
        with self._instance:
            pass
        command_mode_helper.defined_modes_by_prompt.assert_called_once_with(
            self._command_mode
        )
        self._session_pool_manager.get_session.assert_called_once_with(
            self._new_sessions, "|".join(prompts), self._logger
        )
        self._instance._initialize_cli_service.assert_called_once_with(
            session, "|".join(prompts)
        )

    @patch("cloudshell.cli.service.session_pool_context_manager.CommandModeHelper")
    def test_enter_with_exception(self, command_mode_helper):
        self._instance._initialize_cli_service = Mock(side_effect=[Exception()])
        prompts = ["1"]
        command_mode_helper.defined_modes_by_prompt.return_value = Mock()
        command_mode_helper.defined_modes_by_prompt.return_value.keys.return_value = (
            prompts
        )
        session = Mock()
        self._session_pool_manager.get_session.return_value = session
        with self.assertRaises(Exception):
            with self._instance:
                pass
        command_mode_helper.defined_modes_by_prompt.assert_called_once_with(
            self._command_mode
        )
        self._session_pool_manager.get_session.assert_called_once_with(
            self._new_sessions, "|".join(prompts), self._logger
        )
        self._instance._initialize_cli_service.assert_called_once_with(
            session, "|".join(prompts)
        )
        self._session_pool_manager.remove_session(session, self._logger)

    @patch("cloudshell.cli.service.session_pool_context_manager.CommandModeHelper")
    def test_exit_return_session(self, command_mode_helper):
        self._instance._initialize_cli_service = Mock()
        session_value = Mock()
        self._session_pool_manager.get_session.return_value = session_value
        with self._instance:
            pass

        self._session_pool_manager.return_session.assert_called_once_with(
            session_value, self._logger
        )

    @patch("cloudshell.cli.service.session_pool_context_manager.CommandModeHelper")
    def test_exit_remove_session_on_exception(self, command_mode_helper):
        self._instance._initialize_cli_service = Mock()
        session_value = Mock()
        self._session_pool_manager.get_session.return_value = session_value
        exception = Exception
        with self.assertRaises(exception):
            with self._instance:
                raise exception(self.__class__.__name__, "test")
        self._session_pool_manager.remove_session.assert_called_once_with(
            session_value, self._logger
        )

    @patch("cloudshell.cli.service.session_pool_context_manager.CommandModeHelper")
    def test_exit_return_session_on_ignored_exception(self, command_mode_helper):
        self._instance._initialize_cli_service = Mock()
        session_value = Mock()
        self._session_pool_manager.get_session.return_value = session_value
        exception = CommandExecutionException
        with self.assertRaises(exception):
            with self._instance:
                raise exception(self.__class__.__name__, "test")
        self._session_pool_manager.return_session.assert_called_once_with(
            session_value, self._logger
        )

    @patch("cloudshell.cli.service.session_pool_context_manager.CommandModeHelper")
    def test_exit_remove_session_on_inactive(self, command_mode_helper):
        self._instance._initialize_cli_service = Mock()
        session_value = Mock()
        session_value.active.return_value = False
        self._session_pool_manager.get_session.return_value = session_value
        with self._instance:
            pass
        self._session_pool_manager.remove_session.assert_called_once_with(
            session_value, self._logger
        )
