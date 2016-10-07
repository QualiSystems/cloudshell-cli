from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.cli_operations_impl import CliOperationsImpl as CliOperations


class SessionPoolContextManager(object):
    """
    Get and return session from pool and change mode if specified
    """

    def __init__(self, session_pool, session_type, connection_attrs, command_mode, logger):
        """
        :param session_pool:
        :param session_type:
        :param connection_attrs:
        :param command_mode:
        :param logger:
        """

        self._session_pool = session_pool
        self._command_mode = command_mode
        self._logger = logger
        self._session_type = session_type
        self._connection_attrs = connection_attrs

        self._cli_operations = None

    def __enter__(self):
        prompts_re = CommandMode.modes_pattern()
        session = self._session_pool.get_session(logger=self._logger, prompt=prompts_re,
                                                 session_type=self._session_type,
                                                 connection_attrs=self._connection_attrs)
        self._cli_operations = CliOperations(session, self._command_mode, self._logger)
        return self._cli_operations

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session_pool.return_session(self._cli_operations.session, self._logger)
