from cloudshell.cli.session_factory import SessionFactory, SessionFactoryException
from cloudshell.cli import cli_session_type
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.cli.session.tcp_session import TCPSession


class CLISessionFactory(SessionFactory):
    DEFINED_SESSIONS = {cli_session_type.SSH: SSHSession, cli_session_type.TELNET: TelnetSession,
                        cli_session_type.TCP: TCPSession}

    def __init__(self, defined_sessions=DEFINED_SESSIONS):
        self._defined_sessions = defined_sessions

    def new_session(self, prompt, logger, auth=None, **session_attributes):
        if auth.session_type in self._defined_sessions:
            session = self._defined_sessions[auth.session_type](logger=logger, auth=auth,**session_attributes)
            session.connect(prompt, logger)
            logger.debug('Created new {} session'.format(auth.session_type))
            return session
        else:
            raise SessionFactoryException(self.__class__.__name__, 'Session type does not defined')
