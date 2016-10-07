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
        try:
            session = session_type(logger=logger, **connection_attrs)
            session.connect(prompt, logger)
            logger.debug('Created new {} session'.format(session_type.__class__.__name__))
            return session
        except Exception as e:
            logger.debug(e)
            raise SessionFactoryException(self.__class__.__name__, 'Failed to create new session, see logs for details')
