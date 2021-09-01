import logging
import sys

from cloudshell.cli.profiles.ssh.ssh_factory import SSHSessionFactory
from cloudshell.cli.session.basic_session.helper.send_receive import send_line
from cloudshell.cli.session.processing.actions.action_map import ActionMap, Action
from cloudshell.cli.session.processing.core.action_processor import ActionProcessor
from cloudshell.cli.session.processing.core.entities import Command

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

if __name__ == '__main__':
    hostname = "192.168.8.203"
    username = "quali"
    password = "Password1"
    logger = logging.getLogger("CLI")

    session = SSHSessionFactory().create_session(logger=logger, hostname=hostname, username=username, password=password)

    advanced_session = ActionProcessor(session, logger)
    print(advanced_session.send_command(Command("dmesg|more", action_map=ActionMap([Action(r"--More--", lambda s: send_line(s, ""), )]), detect_loops=False)))
