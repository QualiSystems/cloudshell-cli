from unittest import TestCase

from cloudshell.cli.service.cli_exceptions import CommandExecutionException

from cloudshell.cli.session_pool_context_manager import SessionPoolContextManager

from mock import MagicMock as Mock, patch


class TestSessionPoolContextManager(TestCase):
    def setUp(self):
        self._session_pool_manager = Mock()
        self._logger = Mock()
        self._session_type = Mock()
        self._connection_attrs = Mock()
        self._command_mode = Mock()

    @patch('cloudshell.cli.session_pool_context_manager.CommandMode')
    @patch('cloudshell.cli.session_pool_context_manager.CliOperations')
    def test_enter_get_prompt(self, cli_operations, command_mode):
        with SessionPoolContextManager(self._session_pool_manager, self._session_type, self._connection_attrs,
                                       self._command_mode, self._logger) as session:
            pass
        command_mode.modes_pattern.assert_called_once()

    @patch('cloudshell.cli.session_pool_context_manager.CommandMode')
    @patch('cloudshell.cli.session_pool_context_manager.CliOperations')
    def test_enter_get_session(self, cli_operations, command_mode):
        group_pattern = Mock()
        command_mode.modes_pattern.return_value = group_pattern
        with SessionPoolContextManager(self._session_pool_manager, self._session_type, self._connection_attrs,
                                       self._command_mode, self._logger) as session:
            pass
        self._session_pool_manager.get_session.assert_called_once_with(logger=self._logger, prompt=group_pattern,
                                                                       session_type=self._session_type,
                                                                       connection_attrs=self._connection_attrs)

    @patch('cloudshell.cli.session_pool_context_manager.CommandMode')
    @patch('cloudshell.cli.session_pool_context_manager.CliOperations')
    def test_enter_create_cli_operations(self, cli_operations, command_mode):
        group_pattern = Mock()
        command_mode.modes_pattern.return_value = group_pattern
        session_value = Mock()
        self._session_pool_manager.get_session.return_value = session_value
        with SessionPoolContextManager(self._session_pool_manager, self._session_type, self._connection_attrs,
                                       self._command_mode, self._logger) as session:
            pass
        cli_operations.assert_called_once_with(session_value, self._command_mode, self._logger)

    @patch('cloudshell.cli.session_pool_context_manager.CommandMode')
    @patch('cloudshell.cli.session_pool_context_manager.CliOperations')
    def test_exit_return_session(self, cli_operations, command_mode):
        group_pattern = Mock()
        command_mode.modes_pattern.return_value = group_pattern
        session_value = Mock()
        self._session_pool_manager.get_session.return_value = session_value
        with SessionPoolContextManager(self._session_pool_manager, self._session_type, self._connection_attrs,
                                       self._command_mode, self._logger) as session:
            pass

        self._session_pool_manager.return_session.assert_called_once_with(session_value, self._logger)

    @patch('cloudshell.cli.session_pool_context_manager.CommandMode')
    @patch('cloudshell.cli.session_pool_context_manager.CliOperations')
    def test_exit_remove_session_on_exception(self, cli_operations, command_mode):
        group_pattern = Mock()
        command_mode.modes_pattern.return_value = group_pattern
        session_value = Mock()
        self._session_pool_manager.get_session.return_value = session_value
        exception = Exception
        with self.assertRaises(exception):
            with SessionPoolContextManager(self._session_pool_manager, self._session_type, self._connection_attrs,
                                           self._command_mode, self._logger) as session:
                raise exception(self.__class__.__name__, 'test')
        self._session_pool_manager.remove_session.assert_called_once_with(session_value, self._logger)

    @patch('cloudshell.cli.session_pool_context_manager.CommandMode')
    @patch('cloudshell.cli.session_pool_context_manager.CliOperations')
    def test_exit_return_session_on_ignored_exception(self, cli_operations, command_mode):
        group_pattern = Mock()
        command_mode.modes_pattern.return_value = group_pattern
        session_value = Mock()
        self._session_pool_manager.get_session.return_value = session_value
        exception = CommandExecutionException
        with self.assertRaises(exception):
            with SessionPoolContextManager(self._session_pool_manager, self._session_type, self._connection_attrs,
                                           self._command_mode, self._logger) as session:
                raise exception(self.__class__.__name__, 'test')
        self._session_pool_manager.return_session.assert_called_once_with(session_value, self._logger)
