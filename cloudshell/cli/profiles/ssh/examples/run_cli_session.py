import logging
import sys

from cloudshell.cli.profiles.ssh.ssh_factory import SSHSessionFactory
from cloudshell.cli.session.processing.core.command_processor import CommandProcessor
from cloudshell.cli.session.processing.core.entities import Command

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

if __name__ == '__main__':
    hostname = "192.168.8.203"
    username = "quali"
    password = "Password1"
    logger = logging.getLogger("CLI")

    session = SSHSessionFactory().create_session(logger=logger, hostname=hostname, username=username, password=password)

    command_processor = CommandProcessor(session, logger)
    print(command_processor.send_command(Command("ls")))
    print(command_processor.switch_prompt(Command("sh")))  # switch to sh
    print(command_processor.send_command(Command("ls")))
    print(command_processor.switch_prompt(Command("exit")))  # back to bash
    print(command_processor.send_command(Command("ls")))
