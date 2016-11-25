from unittest import TestCase
from cloudshell.cli.cli_service_impl import CommandModeContextManager
from mock import Mock


class TestCommandModeContextManager(TestCase):
    def setUp(self):
        self._cli_operations = Mock()
        self._command_mode = Mock()
        self._logger = Mock()

    def test_init(self):
        mandatory_attributes = ['_logger', '_previous_mode', '_cli_operations', '_command_mode']
        instance = CommandModeContextManager(self._cli_operations, self._command_mode, self._logger)
        self.assertTrue(len(set(mandatory_attributes).difference(set(instance.__dict__.keys()))) == 0)


class TestCliOperationsImpl(TestCase):
    def setUp(self):
        self._logger = Mock()
