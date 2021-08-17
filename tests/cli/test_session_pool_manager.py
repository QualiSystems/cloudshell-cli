from unittest import TestCase

from cloudshell.cli.service.session_pool_manager import (
    SessionPoolException,
    SessionPoolManager,
)

try:
    from unittest.mock import MagicMock, Mock
except ImportError:
    from mock import MagicMock, Mock


class TestSessionPoolManager(TestCase):
    def setUp(self):
        self._session_manager = Mock()
        self._pool = Mock()
        self._condition = MagicMock()
        self._session_pool_manager = SessionPoolManager(
            session_manager=self._session_manager, pool=self._pool
        )
        self._session_pool_manager._session_condition = self._condition
        self._logger = Mock()
        self._new_sessions = Mock()
        self._command_mode = Mock()
        self._prompt = Mock()

    def test_get_session_with_condition_enter(self):
        self._pool.empty.return_value = True
        self._pool.maxsize = 4
        self._session_manager.existing_sessions_count.return_value = 0
        self._session_pool_manager._new_session = Mock()
        self._session_pool_manager.get_session(
            self._new_sessions, self._prompt, self._logger
        )
        self._condition.__enter__.assert_called_once()

    def test_get_session_get_from_pool(self):
        self._pool.empty.return_value = False
        self._session_pool_manager._get_from_pool = Mock()
        self._pool.maxsize = 4
        self._session_manager.existing_sessions_count.return_value = 0
        self._session_pool_manager._new_session = Mock()
        self._session_pool_manager.get_session(
            self._new_sessions, self._prompt, self._logger
        )
        self._session_pool_manager._get_from_pool.assert_called_once_with(
            self._new_sessions, self._prompt, self._logger
        )

    def test_get_session_create_new(self):
        self._pool.empty.return_value = True
        self._pool.maxsize = 2
        self._session_manager.existing_sessions_count.return_value = 1
        self._session_pool_manager._new_session = Mock()
        self._session_pool_manager.get_session(
            self._new_sessions, self._prompt, self._logger
        )
        self._session_pool_manager._new_session.assert_called_once_with(
            self._new_sessions, self._prompt, self._logger
        )

    def test_get_session_condition_wait_raises(self):
        self._pool.empty.return_value = True
        self._pool.maxsize = 1
        self._session_manager.existing_sessions_count.return_value = 1
        self._session_pool_manager._new_session = Mock()
        pool_timeout = 1
        self._session_pool_manager._pool_timeout = pool_timeout

        exception = SessionPoolException
        with self.assertRaises(exception):
            self._session_pool_manager.get_session(
                self._new_sessions, self._prompt, self._logger
            )
            self._condition.wait.assert_called_once_with(pool_timeout)

    def test_get_session_with_condition_exit(self):
        prompt = Mock()
        self._pool.maxsize = 4
        self._session_manager.existing_sessions_count.return_value = 0
        self._session_pool_manager._new_session = Mock()
        self._session_pool_manager.get_session(self._new_sessions, prompt, self._logger)
        self._condition.__exit__.assert_called_once()

    def test_remove_session_with_condition_enter(self):
        session = Mock()
        self._session_pool_manager.remove_session(session, self._logger)
        self._condition.__enter__.assert_called_once()

    def test_remove_session_call(self):
        session = Mock()
        self._session_pool_manager.remove_session(session, self._logger)
        self._session_manager.remove_session.assert_called_once_with(
            session, self._logger
        )

    def test_remove_session_condition_notify(self):
        session = Mock()
        self._session_pool_manager.remove_session(session, self._logger)
        self._condition.notify.assert_called_once()

    def test_remove_session_with_condition_exit(self):
        session = Mock()
        self._session_pool_manager.remove_session(session, self._logger)
        self._condition.__exit__.assert_called_once()

    def test_return_session_with_condition_enter(self):
        session = Mock()
        self._session_pool_manager.return_session(session, self._logger)
        self._condition.__enter__.assert_called_once()

    def test_return_session_call(self):
        session = Mock()
        self._session_pool_manager.return_session(session, self._logger)
        self._pool.put.assert_called_once_with(session)

    def test_return_session_condition_notify(self):
        session = Mock()
        self._session_pool_manager.return_session(session, self._logger)
        self._condition.notify.assert_called_once()

    def test_return_session_with_condition_exit(self):
        session = Mock()
        self._session_pool_manager.return_session(session, self._logger)
        self._condition.__exit__.assert_called_once()

    def test__new_session_called(self):
        prompt = Mock()
        self._session_pool_manager._new_session(
            self._new_sessions, prompt, self._logger
        )
        self._session_manager.new_session.assert_called_once_with(
            self._new_sessions, prompt, self._logger
        )

    def test__new_session_has_attr_new_session_true(self):
        prompt = Mock()
        session = self._session_pool_manager._new_session(
            self._new_sessions, prompt, self._logger
        )
        self.assertTrue(hasattr(session, "new_session") and session.new_session)

    def test__get_from_pool_called_get(self):
        prompt = Mock()
        self._session_pool_manager._get_from_pool(
            self._new_sessions, prompt, self._logger
        )
        self._pool.get.assert_called_once_with(False)

    def test__get_from_pool_is_compatible_called(self):
        prompt = Mock()
        session = Mock()
        self._pool.get.return_value = session
        self._session_pool_manager._get_from_pool(
            self._new_sessions, prompt, self._logger
        )
        self._session_manager.is_compatible.assert_called_once_with(
            session, self._new_sessions, self._logger
        )

    def test__get_from_pool_remove_called(self):
        prompt = Mock()
        self._session_manager.is_compatible.return_value = False
        self._session_pool_manager.remove_session = Mock()
        session = Mock()
        self._pool.get.return_value = session
        self._session_pool_manager._get_from_pool(
            self._new_sessions, prompt, self._logger
        )
        self._session_pool_manager.remove_session.assert_called_once_with(
            session, self._logger
        )

    def test__get_from_pool_new_session_called(self):
        prompt = Mock()
        self._session_manager.is_compatible.return_value = False
        self._session_pool_manager.remove_session = Mock()
        self._session_pool_manager._new_session = Mock()
        session = Mock()
        self._pool.get.return_value = session
        self._session_pool_manager._get_from_pool(
            self._new_sessions, prompt, self._logger
        )
        self._session_pool_manager._new_session.assert_called_once_with(
            self._new_sessions, prompt, self._logger
        )
