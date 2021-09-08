import logging
from logging import Logger
from typing import TYPE_CHECKING, Optional

from cloudshell.cli.process.command.command_processor import CommandProcessor
from cloudshell.cli.profiles.ssh.ssh_session import SSHSession
from cloudshell.cli.process.command.entities import Command
from cloudshell.cli.session.core.factory import AbstractSessionFactory

if TYPE_CHECKING:
    from cloudshell.cli.session.core.session import Session
    from cloudshell.cli.session.prompt.prompt import Prompt

logger = logging.getLogger(__name__)


class SSHSessionFactory(AbstractSessionFactory):
    def __init__(self, hostname, username, password, port=22, pkey=None,
                 pkey_passphrase=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.pkey = pkey
        self.pkey_passphrase = pkey_passphrase

    def get_session(self, prompt: Optional["Prompt"] = None) -> SSHSession:
        logger.debug("Create SSH session.")
        session = SSHSession(hostname=self.hostname,
                             port=self.port,
                             username=self.username,
                             password=self.password,
                             pkey=self.pkey,
                             pkey_passphrase=self.pkey_passphrase)
        self._connect_actions(session, prompt)
        return session

    def _connect_actions(self, session: "Session", prompt: Optional["Prompt"]) -> None:
        logger.debug("Connect actions")
        session.connect()
        advanced_session = CommandProcessor(session)
        advanced_session.send_command(Command("", prompt))

    def get_type(self):
        return SSHSession.SESSION_TYPE

    def compatible(self, session: "Session"):
        if isinstance(session, SSHSession) and \
                session.hostname == self.hostname and \
                session.port == self.port:
            # the rest should be added
            return True
