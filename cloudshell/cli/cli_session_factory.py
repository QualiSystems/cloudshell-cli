from cloudshell.cli.session_factory import SessionFactory, SessionFactoryException


class CLISessionFactory(SessionFactory):
    def new_session(self, session_type, connection_attrs, prompt, logger):
        try:
            session = session_type(logger=logger, **connection_attrs)
            session.connect(prompt, logger)
            logger.debug('Created new {} session'.format(session))
            return session
        except Exception as e:
            logger.debug(e.message)
            raise SessionFactoryException(self.__class__.__name__, e.message)
