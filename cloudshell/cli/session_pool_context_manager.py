from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cli.session_pool import SessionPool


class SessionPoolContextManager(object):
    """
    Get and return session from pool
    """

    def __init__(self, session_pool, **session_attributes):
        """
        :param session_pool:
        :type session_pool: SessionPool
        """
        self._session_pool = session_pool
        self._session_attributes = session_attributes
        self._session = None

    def __enter__(self):
        self._session = self._session_pool.get_session(**self._session_attributes)
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session_pool.return_session(self._session)
