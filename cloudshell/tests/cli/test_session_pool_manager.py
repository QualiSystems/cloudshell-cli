from unittest import TestCase

from cloudshell.cli.session_pool_manager import SessionPoolManager
from mock import Mock


class TestSessionPoolManager(TestCase):
    def setUp(self):
        self._session_manager = Mock()
        self._pool = Mock()
        self._session_pool_manager = SessionPoolManager(session_manager=self._session_manager, pool=self._pool)
        self._logger = Mock()
        self._session_type = Mock()
        self._connection_attrs = Mock()
        self._command_mode = Mock()
        self._prompt = Mock()

    def test_get_session_get_from_pool(self):
        self._pool.empty.return_value = False
        self._session_pool_manager._get_from_pool = Mock()
        session = self._session_pool_manager.get_session(self._session_type, self._connection_attrs, self._prompt,
                                                         self._logger)
        self._session_pool_manager._get_from_pool.assert_called_once_with(self._session_type, self._connection_attrs,
                                                                          self._prompt, self._logger)

    def test_get_session_create_new(self):
        self._pool.empty.return_value = True
        self._pool.maxsize = 2
        self._session_manager.existing_sessions_count.return_value = 1
        self._session_pool_manager._new_session = Mock()
        session = self._session_pool_manager.get_session(self._session_type, self._connection_attrs, self._prompt,
                                                         self._logger)
        self._session_pool_manager._new_session.assert_called_once_with(self._session_type, self._connection_attrs,
                                                                        self._prompt, self._logger)

    def test_get_session_condition_wait_call(self):
        self._pool.empty.return_value = True
        self._pool.maxsize = 1
        self._session_manager.existing_sessions_count.return_value = 1
        self._session_pool_manager._new_session = Mock()
        self._session_pool_manager._pool_timeout

        session = self._session_pool_manager.get_session(self._session_type, self._connection_attrs, self._prompt,
                                                         self._logger)
        self._session_pool_manager._new_session.assert_called_once_with(self._session_type, self._connection_attrs,
                                                                        self._prompt, self._logger)
