from cloudshell.cli.cli_exception import CliException
from cloudshell.cli.session_factory import SessionFactory


class SessionFactoryException(CliException):
    pass


class CLISessionFactory(SessionFactory):
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
        else:
            session_type_list = [session_type]

        return self._auto_session(session_type_list, connection_attrs, prompt, logger)

    def _defined_session(self, session_type, connection_attrs, prompt, logger):
        try:
            session = session_type(logger=logger, **connection_attrs)
            session.connect(prompt, logger)
            logger.debug('Created new {} session'.format(session_type.__class__.__name__))
        except Exception as e:
            logger.debug(e)
            session = None
        return session

    def _auto_session(self, session_type_list, connection_attrs, prompt, logger):
        session = None
        for session_type in session_type_list:
            session = self._defined_session(session_type, connection_attrs, prompt, logger)
            if session:
                break
        if not session:
            raise SessionFactoryException(self.__class__.__name__,
                                          'Failed to create new session for type {}, see logs for details'.format(
                                              ','.join([x.__class__.__name__ for x in session_type_list])))
        return session
