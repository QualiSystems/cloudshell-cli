from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.cli_operations_impl import CliOperationsImpl as CliOperations
from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cli.service.cli_exceptions import CommandExecutionException


class SessionPoolContextManager(object):
    """
    Get and return session from pool and change mode if specified
    """

    IGNORE_EXCEPTIONS = [CommandExecutionException]

    def __init__(self, session_pool, new_sessions, command_mode, logger):
        """
        :param session_pool:
        :param sessions
        :param command_mode:
        :type command_mode: CommandMode
        :param logger:
        """

        self._session_pool = session_pool
        self._command_mode = command_mode
        self._logger = logger

        self._new_sessions = new_sessions

        self._session = None

    def __enter__(self):
        """
        :return:
        :rtype: CliOperations
        """
        prompts_re = r'|'.join(CommandModeHelper.defined_modes_by_prompt(self._command_mode).keys())
        self._session = self._session_pool.get_session(new_sessions=self._new_sessions, prompt=prompts_re,
                                                       logger=self._logger)
        return CliOperations(self._session, self._command_mode, self._logger)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and exc_type not in self.IGNORE_EXCEPTIONS:
            self._session_pool.remove_session(self._session, self._logger)
        else:
            self._session_pool.return_session(self._session, self._logger)
