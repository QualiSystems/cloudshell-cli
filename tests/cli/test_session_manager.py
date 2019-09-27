from unittest import TestCase

from cloudshell.cli.service.session_manager_impl import (
    SessionManagerException,
    SessionManagerImpl,
)

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestSessionManager(TestCase):
    def setUp(self):
        self._session_manager = SessionManagerImpl()
        self._logger = Mock()
        self._new_session = Mock()
        self._prompt = Mock()

    def test_new_sessions_new_sessions_not_list(self):
        self.assertTrue(
            self._session_manager.new_session(
                self._new_session, self._prompt, self._logger
            )
            == self._new_session
        )

    def test_new_sessions_new_sessions_call_connect(self):
        new_sessions = [self._new_session]
        self._session_manager.new_session(new_sessions, self._prompt, self._logger)
        self._new_session.connect.assert_called_once_with(self._prompt, self._logger)

    def test_new_sessions_new_sessions_add_to_existing_sessions(self):
        new_sessions = [self._new_session]
        self._session_manager.new_session(new_sessions, self._prompt, self._logger)
        self.assertTrue(self._new_session in self._session_manager._existing_sessions)

    def test_new_sessions_new_sessions_catch_exception(self):
        self._new_session.connect = Mock(side_effect=Exception())
        self._new_session.session_type = "test"
        new_sessions = [self._new_session]
        exception = SessionManagerException
        with self.assertRaises(exception):
            self._session_manager.new_session(new_sessions, self._prompt, self._logger)

    def test_existing_sessions_count(self):
        self._session_manager._existing_sessions.append(Mock())
        self.assertTrue(self._session_manager.existing_sessions_count() == 1)

    def test_remove_session(self):
        session = Mock()
        self._session_manager._existing_sessions.append(session)
        self._session_manager.remove_session(session, self._logger)
        self.assertTrue(session not in self._session_manager._existing_sessions)

    def test_is_compatible_raise_exception(self):
        session = Mock()
        exception = SessionManagerException
        with self.assertRaises(exception):
            self._session_manager.is_compatible(
                session, [self._new_session], self._logger
            )

    def test_is_compatible_true(self):
        session = self._new_session
        self._session_manager._existing_sessions.append(self._new_session)
        self.assertTrue(
            self._session_manager.is_compatible(
                session, [self._new_session], self._logger
            )
        )
