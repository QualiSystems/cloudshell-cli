import logging
from unittest import TestCase
from cloudshell.cli.connection_manager import ConnectionManager
import inject
from inject import Binder
import types


class TestConnectionManager(TestCase):

    def test_must_receive_a_config_for_init(self):
        self._configure_injector()
        try:
            ConnectionManager(None,None)
            self.fail("Managed to get a manager without config")
        except Exception as e:
            self.assertEquals(e.message,"not config provided")


    def _configure_bindings(self, binder):
        binder.bind_to_constructor('connection_manager', ConnectionManager)
        config = types.ModuleType("test_config")
        config.CONNECTION_MAP = {}
        config.SESSION_POOL_SIZE = 3
        config.DEFAULT_PROMPT = ""
        config.CONNECTION_TYPE_AUTO = "ssh"
        config.CONNECTION_TYPE = "ssh"
        config.POOL_TIMEOUT = 60

        binder.bind("logger", logging.Logger("test_logger"))

    def _configure_injector(self):
        inject.configure(self._configure_bindings)
