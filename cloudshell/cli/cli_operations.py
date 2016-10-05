from abc import ABCMeta, abstractmethod


class CliOperations(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def send_command(self, command, logger, expected_string=None, *args, **kwargs):
        pass

    @abstractmethod
    def enter_mode(self, command_mode):
        pass
