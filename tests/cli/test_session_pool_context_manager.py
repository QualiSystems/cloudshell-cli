from unittest import TestCase
import unittest

from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.cli.session_pool_context_manager import SessionPoolContextManager
from mock import MagicMock as Mock, patch


class TestSessionPoolContextManager(TestCase):
    def setUp(self):
        self._session_pool_manager = Mock()
        self._logger = Mock()
        self._new_sessions = Mock()
        self._connection_attrs = Mock()
        self._command_mode = Mock()

    @patch('cloudshell.cli.session_pool_context_manager.CommandModeHelper')
    @patch('cloudshell.cli.session_pool_context_manager.CliService')
    def test_enter_get_prompts(self, cli_service, command_mode_helper):
        with SessionPoolContextManager(self._session_pool_manager, self._new_sessions, self._command_mode,
                                       self._logger) as session:
            pass
        command_mode_helper.defined_modes_by_prompt.assert_called_once_with(self._command_mode)

    @patch('cloudshell.cli.session_pool_context_manager.CommandModeHelper')
    @patch('cloudshell.cli.session_pool_context_manager.CliService')
    def test_enter_get_session(self, cli_service, command_mode_helper):
        prompt = '1'
        command_mode_helper.defined_modes_by_prompt.return_value = Mock()
        command_mode_helper.defined_modes_by_prompt.return_value.keys.return_value = prompt
        with SessionPoolContextManager(self._session_pool_manager, self._new_sessions, self._command_mode,
                                       self._logger) as session:
            pass
        self._session_pool_manager.get_session.assert_called_once_with(logger=self._logger,
                                                                       prompt='|'.join(prompt),
                                                                       new_sessions=self._new_sessions)

    @patch('cloudshell.cli.session_pool_context_manager.CommandModeHelper')
    @patch('cloudshell.cli.session_pool_context_manager.CliService')
    def test_enter_create_cli_service(self, cli_service, command_mode_helper):
        session_value = Mock()
        self._session_pool_manager.get_session.return_value = session_value
        with SessionPoolContextManager(self._session_pool_manager, self._new_sessions, self._command_mode,
                                       self._logger) as session:
            pass
        cli_service.assert_called_once_with(session_value, self._command_mode, self._logger)

    @patch('cloudshell.cli.session_pool_context_manager.CommandModeHelper')
    @patch('cloudshell.cli.session_pool_context_manager.CliService')
    def test_exit_return_session(self, cli_service, command_mode_helper):
        session_value = Mock()
        self._session_pool_manager.get_session.return_value = session_value
        with SessionPoolContextManager(self._session_pool_manager, self._new_sessions, self._command_mode,
                                       self._logger) as session:
            pass

        self._session_pool_manager.return_session.assert_called_once_with(session_value, self._logger)

    @patch('cloudshell.cli.session_pool_context_manager.CommandModeHelper')
    @patch('cloudshell.cli.session_pool_context_manager.CliService')
    def test_exit_remove_session_on_exception(self, cli_service, command_mode_helper):
        session_value = Mock()
        self._session_pool_manager.get_session.return_value = session_value
        exception = Exception
        with self.assertRaises(exception):
            with SessionPoolContextManager(self._session_pool_manager, self._new_sessions, self._command_mode,
                                           self._logger) as session:
                raise exception(self.__class__.__name__, 'test')
        self._session_pool_manager.remove_session.assert_called_once_with(session_value, self._logger)

    @patch('cloudshell.cli.session_pool_context_manager.CommandModeHelper')
    @patch('cloudshell.cli.session_pool_context_manager.CliService')
    def test_exit_return_session_on_ignored_exception(self, cli_service, command_mode_helper):
        session_value = Mock()
        self._session_pool_manager.get_session.return_value = session_value
        exception = CommandExecutionException
        with self.assertRaises(exception):
            with SessionPoolContextManager(self._session_pool_manager, self._new_sessions, self._command_mode,
                                           self._logger) as session:
                raise exception(self.__class__.__name__, 'test')
        self._session_pool_manager.return_session.assert_called_once_with(session_value, self._logger)
