from unittest import TestCase
from mock import Mock


class TestCommandMode(TestCase):
    def setUp(self):
        self._session = Mock()
        self._command_mode = Mock()
        self._logger = Mock()
