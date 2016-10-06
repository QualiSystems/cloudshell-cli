from cloudshell.cli.session_factory import SessionFactory, SessionFactoryException



class CLISessionFactory(SessionFactory):


    def __init__(self):
        pass

    def new_session(self, prompt, logger, session=None,auth=None,**session_attributes):
        try:
            session = session(logger=logger, auth=auth,**session_attributes)
            session.connect(prompt, logger)
            logger.debug('Created new {} session'.format(session))
            return session
        except Exception as e:
            raise SessionFactoryException(self.__class__.__name__, 'Session class is not defined')
