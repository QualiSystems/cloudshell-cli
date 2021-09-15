import logging
from typing import TYPE_CHECKING, Optional, Type

from cloudshell.cli.configurator import FromResourceConfig
from cloudshell.cli.process.command.processor import CommandProcessor
from cloudshell.cli.process.command.entities import Command
from cloudshell.cli.session.core.exception import SessionFactoryException
from cloudshell.cli.session.core.factory import AbstractSessionFactory

if TYPE_CHECKING:
    from cloudshell.cli.session.core.session import Session
    from cloudshell.shell.core.driver_context import ReservationContextDetails
    from cloudshell.shell.standards.resource_config_generic_models import GenericCLIConfig
    from cloudshell.cli.profiles.ssh.ssh_session import SSHSession, SSHParams, SSHConfig

logger = logging.getLogger(__name__)


class SSHSessionFactory(FromResourceConfig):
    def __init__(self, session_class: Type[Session], session_config: Optional["SSHConfig"] = None):
        AbstractSessionFactory.__init__(self, session_class, session_config)
        self._params: Optional["SSHParams"] = None

    def get_params(self) -> "SSHParams":
        if self._params is None:
            raise SessionFactoryException("Params not defined.")
        return self._params

    def init_from_resource_conf(self, resource_config: "GenericCLIConfig",
                                reservation_context: "ReservationContextDetails"):

        access_key = ""
        if reservation_context and reservation_context.cloud_info_access_key:
            access_key = reservation_context.cloud_info_access_key
        self._params = SSHParams(hostname=resource_config.address,
                                 username=resource_config.user,
                                 password=resource_config.password,
                                 port=resource_config.cli_tcp_port,
                                 pkey=access_key)

    def get_active_session(self) -> "SSHSession":
        logger.debug("Create SSH session.")
        session = self.session_class(self.get_params(), self.config)
        session.connect()
        self._connect_actions(session)
        return session

    def _connect_actions(self, session: "Session") -> None:
        logger.debug("Connect actions")
        advanced_session = CommandProcessor(session)
        advanced_session.send_command(Command(""))

    def compatible(self, session: "Session") -> bool:
        return (super(SSHSessionFactory, self).compatible(session)
                and self.get_params() == session.params)
