import logging
import sys

from cloudshell.cli.process.command.processor import CommandProcessor
from cloudshell.cli.process.command.entities import Command
from cloudshell.cli.process.mode.command_mode import CommandMode
from cloudshell.cli.process.mode.manager import CommandModeContextManager
from cloudshell.cli.profiles.ssh.ssh_factory import SSHSessionFactory
from cloudshell.cli.session.manage.session_pool import SessionPoolManager
from cloudshell.cli.session.prompt.prompt import Prompt

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

if __name__ == '__main__':
    hostname = "192.168.8.203"
    username = "quali"
    password = "Password1"
    logger = logging.getLogger("CLI")

    bash_mode = CommandMode(prompt=Prompt(r"\s*.+\$\s*$"))
    sh_mode = CommandMode(prompt=Prompt(r"\s*\$\s*$"), enter_command=Command("sh"), exit_command=Command("exit"), parent_mode=bash_mode)
    factories = [SSHSessionFactory(hostname=hostname, username=username, password=password)]
    pool_manager = SessionPoolManager()


    with CommandModeContextManager(pool_manager, factories, sh_mode) as command_processor:

        print(command_processor.send_command(Command("ls -lha")))

    with CommandModeContextManager(pool_manager, factories, bash_mode) as command_processor:
        print(command_processor.send_command(Command("ls -lha")))

    # print(command_processor.switch_prompt(Command("sh")))  # switch to sh
    # print(command_processor.send_command(Command("ls")))
    # print(command_processor.switch_prompt(Command("exit")))  # back to bash
    # print(command_processor.send_command(Command("ls")))
    # pool_manager.return_session(session)
