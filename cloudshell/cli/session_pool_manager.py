from cloudshell.cli.session_pool import SessionPool
from cloudshell.cli.cli import Cli
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.cli.session.tcp_session import TCPSession


class SessionPoolManager(SessionPool):
    DEFINED_SESSIONS = {Cli.SSH: SSHSession,
                        Cli.TELNET: TelnetSession,
                        Cli.TCP: TCPSession}

    def get_session(self, session_type, command_mode, **session_args):
        pass

    def remove_session(self, session):
        pass

    def return_session(self, session):
        pass

    def _new_session(self, session_type, **session_args):
        pass
