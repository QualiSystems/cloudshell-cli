import logging
import sys

from cloudshell.cli.manage.session_pool import SessionPoolManager
from cloudshell.cli.process.command.command_processor import CommandProcessor
from cloudshell.cli.process.command.entities import Command
from cloudshell.cli.profiles.ssh.ssh_factory import SSHSessionFactory

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

if __name__ == '__main__':
    hostname = "192.168.8.203"
    username = "quali"
    password = "Password1"
    logger = logging.getLogger("CLI")

    factories = [SSHSessionFactory(hostname=hostname, username=username, password=password)]
    pool_manager = SessionPoolManager()
    session = pool_manager.get_session(factories)

    command_processor = CommandProcessor(session)
    print(command_processor.send_command(Command("ls -lha")))
    print(command_processor.switch_prompt(Command("sh")))  # switch to sh
    print(command_processor.send_command(Command("ls")))
    print(command_processor.switch_prompt(Command("exit")))  # back to bash
    print(command_processor.send_command(Command("ls")))
