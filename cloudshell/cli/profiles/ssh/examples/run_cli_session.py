import logging
import sys

from cloudshell.cli.profiles.ssh.ssh_factory import SSHSessionFactory
from cloudshell.cli.session.advanced_session.core.advanced_session import AdvancedSession
from cloudshell.cli.session.advanced_session.core.entities import Command

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

if __name__ == '__main__':
    hostname = "192.168.8.203"
    username = "admin"
    password = "Password!"
    logger = logging.getLogger("CLI")

    session = SSHSessionFactory().create_session(logger=logger, hostname=hostname, username=username, password=password)

    advanced_session = AdvancedSession(session, logger)
    print(advanced_session.send_command(Command("ls")))
