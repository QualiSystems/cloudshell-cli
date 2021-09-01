from cloudshell.cli.profiles.ssh.ssh_session import SSHSession
from cloudshell.cli.session.basic_session.core.session_factory import AbstractSessionFactory
from cloudshell.cli.session.processing.core.action_processor import ActionProcessor
from cloudshell.cli.session.processing.core.entities import Command


class SSHSessionFactory(AbstractSessionFactory):

    def create_session(self, logger, hostname, username, password, port=22, pkey=None,
                       pkey_passphrase=None) -> SSHSession:
        session = SSHSession(hostname=hostname,
                             port=port,
                             username=username,
                             password=password,
                             pkey=pkey,
                             pkey_passphrase=pkey_passphrase)
        self._connect_actions(session, logger)
        return session

    def _connect_actions(self, session, logger):
        session.connect()
        advanced_session = ActionProcessor(session, logger)
        advanced_session.send_command(Command(""))
