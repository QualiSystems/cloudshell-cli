from connect_to_switch.SwitchClihandler import SwitchCliHandler

from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.shell.standards.core import (
    ResourceCommandContext,
    ResourceContextDetails,
)

from cloudshell.cli.cli import CLI
from cloudshell.cli.session_pool_manager import SessionPoolManager

logger = get_qs_logger()


def create_context():
    context = ResourceCommandContext()
    context.resource = ResourceContextDetails()
    context.resource.name = "Switch for Demo"
    context.resource.address = "<IP>"
    context.resource.attributes = {}
    context.resource.attributes["CLI Connection Type"] = "SSH"
    context.resource.attributes["User"] = "<username>"
    context.resource.attributes["AdminUser"] = "admin"
    context.resource.attributes["Console Password"] = "<password>"
    context.resource.attributes["Password"] = "<password>"
    context.resource.attributes["Enable Password"] = "<password>"
    context.resource.attributes["Sessions Concurrency Limit"] = 2

    return context


if __name__ == "__main__":
    context = create_context()

    pool = SessionPoolManager(max_pool_size=1)
    cli = CLI(session_pool=pool)
    cli_handler = SwitchCliHandler(cli, context, logger)

    with cli_handler.get_cli_service(cli_handler.enable_mode) as session:
        out = session.send_command("echo checking switch")
        with session.enter_mode(cli_handler.config_mode) as config_session:
            out = config_session.send_command("echo checking switch")
            print(out)  # noqa: T001
            out = config_session.send_command("echo checking switch")
            print(out)  # noqa: T001
