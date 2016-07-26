from abc import ABCMeta
from abc import abstractmethod


class CliServiceInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def send_command(self, command, expected_str=None, expected_map=None, error_map=None):
        pass

    @abstractmethod
    def send_config_command(self, command, expected_str=None, expected_map=None, error_map=None):
        pass

    @abstractmethod
    def _enter_configuration_mode(self):
        pass

    @abstractmethod
    def exit_configuration_mode(self):
        pass

    @abstractmethod
    def send_command_list(self, commands_list, send_command_func=None, expected_map=None, error_map=None):
        pass

    @abstractmethod
    def commit(self, expected_map):
        pass

    @abstractmethod
    def rollback(self, expected_map):
        pass
