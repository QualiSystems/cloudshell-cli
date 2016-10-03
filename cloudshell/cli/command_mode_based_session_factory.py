from cloudshell.cli.session_factory import SessionFactory, SessionFactoryException
from cloudshell.cli.cli import Cli
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.cli.session.tcp_session import TCPSession


class CommandModeBasedSessionFactory(SessionFactory):
    DEFINED_SESSIONS = {Cli.SSH: SSHSession, Cli.TELNET: TelnetSession, Cli.TCP: TCPSession}

    def __init__(self, defined_sessions=DEFINED_SESSIONS, default_command_mode=None):
        self._defined_sessions = defined_sessions
        self._default_command_mode = default_command_mode

    def new_session(self, session_type=None, prompt=None, logger=None, **session_attributes):
        if session_type in self._defined_sessions:
            session = self._defined_sessions[session_type](logger=logger, **session_attributes)
            session.connect(prompt=prompt, logger=logger)
            logger.debig('Created new {} session'.format(session_type))
        else:
            raise SessionFactoryException(self.__class__.__name__, 'Session type does not defined')
