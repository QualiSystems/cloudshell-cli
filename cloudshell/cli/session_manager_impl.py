from copy import copy

from cloudshell.cli.cli_exception import CliException
from cloudshell.cli.session_manager import SessionManager


class SessionManagerException(CliException):
    pass



class SessionManagerImpl(SessionManager):
    def __init__(self):
        self._existing_sessions_params = {}

    def new_session(self, connection_attrs, prompt, logger):
        """
        Create new session
        :param session_type:
        :param connection_attrs:
        :param prompt:
        :param logger:
        :return:
        """


        return self._suitable_session(connection_attrs, prompt, logger)

    @staticmethod
    def _create_session(connection_attrs, prompt, logger):
        try:
            session = connection_attrs.TYPE(logger=logger, **connection_attrs.__dict__)
            session.connect(prompt, logger)
            logger.debug('Created new {} session'.format(session.session_type))
        except Exception as e:
            logger.debug(e)
            session = None
        return session

    def _suitable_session(self, connection_attrs, prompt, logger):

        session = self._create_session(connection_attrs, prompt, logger)
        if session:
            self._existing_sessions_params[session] = SessionParams(connection_attrs.TYPE, connection_attrs.__dict__)
            return session

        raise SessionManagerException(self.__class__.__name__,
                                      'Failed to create new session for type {}, see logs for details'.format(connection_attrs.TYPE))

    def existing_sessions_count(self):
        """
        Count of existing sessions
        :return:
        :rtype: int
        """
        return len(self._existing_sessions_params)

    def remove_session(self, session, logger):
        """
        Remove session
        :param session:
        :param logger:
        """
        if session in self._existing_sessions_params:
            del (self._existing_sessions_params[session])
            logger.debug('{} session was removed'.format(session.session_type))

    def is_compatible(self, session, connection_attrs, logger):
        """
        Compare session with new session parameters
        :param session:
        :param session_type_list:
        :param connection_attrs:
        :param logger:
        :return:
        """

        if session in self._existing_sessions_params:
            compatible = False

            if connection_attrs == self._existing_sessions_params[session]:
                compatible = True

            return compatible
        else:
            raise SessionManagerException(self.__class__.__name__, 'Unknown session')
