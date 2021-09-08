from abc import ABCMeta, abstractmethod

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})


class CliService(ABC):
    def __init__(self, session, logger):
        """Initialize CLI service.

        :type session: cloudshell.cli.session.session.Session
        :type logger: logging.Logger
        """
        self.session = session
        self._logger = logger

    @abstractmethod
    def send_command(
        self,
        command,
        expected_string=None,
        action_map=None,
        error_map=None,
        logger=None,
        *args,
        **kwargs
    ):
        pass

    @abstractmethod
    def enter_mode(self, command_mode):
        pass

    @abstractmethod
    def reconnect(self, timeout=None):
        pass
