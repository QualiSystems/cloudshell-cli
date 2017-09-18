from cloudshell.cli.cli_service_impl import CliServiceImpl as CliService
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cli.session.expect_session import CommandExecutionException


class SessionPoolContextManager(object):
    """
    Get and return session from pool and change mode if specified
    """

    IGNORED_EXCEPTIONS = [CommandExecutionException]

    def __init__(self, session_pool, new_sessions, command_mode, logger):
        """
        :param session_pool:
        :param new_sessions
        :param command_mode:
        :type command_mode: CommandMode
        :param logger:
        """

        self._session_pool = session_pool
        self._command_mode = command_mode
        self._logger = logger

        self._new_sessions = new_sessions

        self._session = None

    def _initialize_cli_service(self, session, prompt):
        try:
            return CliService(session, self._command_mode, self._logger)
        except:
            session.reconnect(prompt, self._logger)
            return CliService(session, self._command_mode, self._logger)

    def __enter__(self):
        """
        :return:
        :rtype: CliServiceImpl
        """
        prompts_re = r'|'.join(CommandModeHelper.defined_modes_by_prompt(self._command_mode).keys())
        self._session = self._session_pool.get_session(new_sessions=self._new_sessions, prompt=prompts_re,
                                                       logger=self._logger)
        try:
            return self._initialize_cli_service(self._session, prompts_re)
        except:
            self._session_pool.remove_session(self._session, self._logger)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            if exc_type and exc_type not in self.IGNORED_EXCEPTIONS or not self._session.active():
                self._session_pool.remove_session(self._session, self._logger)
            else:
                self._session_pool.return_session(self._session, self._logger)
