import io

import paramiko

from cloudshell.core.logger.qs_logger import get_qs_logger

from cloudshell.cli.cli import CLI
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session_pool_manager import SessionPoolManager


class CliCommandMode(CommandMode):
    PROMPT = r"$"
    ENTER_COMMAND = ""
    EXIT_COMMAND = "exit"

    def __init__(self, context):
        CommandMode.__init__(
            self,
            CliCommandMode.PROMPT,
            CliCommandMode.ENTER_COMMAND,
            CliCommandMode.EXIT_COMMAND,
        )


LOGGER = get_qs_logger()

CommandMode.RELATIONS_DICT = {CliCommandMode: {}}
if __name__ == "__main__":
    pool = SessionPoolManager(max_pool_size=1)
    cli = CLI(session_pool=pool)

    context = type(
        "context",
        (object,),
        {"resource": type("resource", (object,), {"name": "test name"})},
    )

    host = "<AWS-IP>"

    pem_file = open("mykey.pem", "r")
    key_str = pem_file.read()
    keyfile = io.StringIO(key_str)
    mykey = paramiko.RSAKey.from_private_key(keyfile)

    modes = CommandModeHelper.create_command_mode(context)
    default_mode = modes[CliCommandMode]

    session = SSHSession(host, username="<username>", password="", pkey=mykey)
    with cli.get_session(session, default_mode) as default_session:
        out = default_session.send_command("echo Cli Demo connected to AWS Machine")
        print(out)  # noqa T001
