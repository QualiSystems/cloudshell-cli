from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.cli_operations_impl import CliOperationsImpl as CliOperations
from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cli.service.cli_exceptions import CommandExecutionException


class SessionPoolContextManager(object):
    """
    Get and return session from pool and change mode if specified
    """

    IGNORE_EXCEPTIONS = [CommandExecutionException]

    def __init__(self, session_pool, session_type, connection_attrs, command_mode, logger):
        """
        :param session_pool:
        :param session_type:
        :param connection_attrs:
        :param command_mode:
        :type command_mode: CommandMode
        :param logger:
        """

        self._session_pool = session_pool
        self._command_mode = command_mode
        self._logger = logger
        self._session_type = session_type
        self._connection_attrs = connection_attrs

        self._session = None

    def __enter__(self):
        """
        :return:
        :rtype: CliOperationsImpl
        """
        prompts_re = r'|'.join(CommandModeHelper.defined_modes_by_prompt(self._command_mode).keys())
        self._session = self._session_pool.get_session(logger=self._logger, prompt=prompts_re,
                                                       session_type=self._session_type,
                                                       connection_attrs=self._connection_attrs)
        return CliOperations(self._session, self._command_mode, self._logger)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and exc_type not in self.IGNORE_EXCEPTIONS:
            self._session_pool.remove_session(self._session, self._logger)
        else:
            self._session_pool.return_session(self._session, self._logger)
