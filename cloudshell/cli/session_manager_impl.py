from copy import copy

from cloudshell.cli.cli_exception import CliException
from cloudshell.cli.session_manager import SessionManager


class SessionManagerException(CliException):
    pass


class SessionParams(object):
    """
    Holder for session parameters, compare parameters as objects
    """
    EXCLUDE_ATTRIBUTES = ['default_actions']

    def __init__(self, session_type, connection_attrs):
        self.session_type = session_type
        attrs_copy = copy(connection_attrs)
        for attr in self.EXCLUDE_ATTRIBUTES:
            if attr in attrs_copy:
                del attrs_copy[attr]
        self.connection_attrs = attrs_copy

    def __eq__(self, other):
        return self.session_type == other.session_type and self.connection_attrs == other.connection_attrs


class SessionManagerImpl(SessionManager):
    def __init__(self):
        self._existing_sessions_params = {}

    def new_session(self, session_type, connection_attrs, prompt, logger):
        """
        Create new session
        :param session_type:
        :param connection_attrs:
        :param prompt:
        :param logger:
        :return:
        """

        if isinstance(session_type, list):
            session_type_list = session_type
            logger.debug(
                'Session list {} was called'.format(','.join([x.SESSION_TYPE for x in session_type_list])))
        else:
            session_type_list = [session_type]

        return self._suitable_session(session_type_list, connection_attrs, prompt, logger)

    @staticmethod
    def _create_session(session_type, connection_attrs, prompt, logger):
        try:
            session = session_type(logger=logger, **connection_attrs)
            session.connect(prompt, logger)
            logger.debug('Created new {} session'.format(session.session_type))
        except Exception as e:
            logger.debug(e)
            session = None
        return session

    def _suitable_session(self, session_type_list, connection_attrs, prompt, logger):
        for session_type in session_type_list:
            session = self._create_session(session_type, connection_attrs, prompt, logger)
            if session:
                self._existing_sessions_params[session] = SessionParams(session_type, connection_attrs)
                return session

        raise SessionManagerException(self.__class__.__name__,
                                      'Failed to create new session for type {}, see logs for details'.format(
                                          ','.join([x.SESSION_TYPE for x in session_type_list])))

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

    def is_compatible(self, session, session_type_list, connection_attrs, logger):
        """
        Compare session with new session parameters
        :param session:
        :param session_type_list:
        :param connection_attrs:
        :param logger:
        :return:
        """
        if not isinstance(session_type_list, list):
            session_type_list = [session_type_list]

        if session in self._existing_sessions_params:
            compatible = False
            for session_type in session_type_list:
                session_params = SessionParams(session_type, connection_attrs)
                if session_params == self._existing_sessions_params[session]:
                    compatible = True
                    break
            return compatible
        else:
            raise SessionManagerException(self.__class__.__name__, 'Unknown session')
