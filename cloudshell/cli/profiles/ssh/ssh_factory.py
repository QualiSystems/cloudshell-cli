import logging
from typing import TYPE_CHECKING, Type, Optional, Callable

from cloudshell.cli.session.core.factory import FromResourceConfigFactory

if TYPE_CHECKING:
    from cloudshell.shell.core.driver_context import ReservationContextDetails
    from cloudshell.shell.standards.resource_config_generic_models import GenericCLIConfig
    from cloudshell.cli.profiles.ssh.ssh_session import SSHParams
    from cloudshell.cli.session.core.session import Session
    from cloudshell.cli.session.core.connection_params import ConnectionParams
    from cloudshell.cli.session.core.config import SessionConfig

logger = logging.getLogger(__name__)


class SSHFromResourceConfig(FromResourceConfigFactory):

    def __init__(self, session_class: Type["Session"],
                 session_config: Optional["SessionConfig"] = None,
                 params: Optional["ConnectionParams"] = None,
                 connect_actions: Callable[["Session"], None] = None):
        super().__init__(session_class, session_config, params, connect_actions)

    def init_from_resource_conf(self, resource_config: "GenericCLIConfig",
                                reservation_context: "ReservationContextDetails"):
        access_key = ""
        if reservation_context and reservation_context.cloud_info_access_key:
            access_key = reservation_context.cloud_info_access_key
        self.set_params(SSHParams(hostname=resource_config.address,
                                  username=resource_config.user,
                                  password=resource_config.password,
                                  port=resource_config.cli_tcp_port,
                                  pkey=access_key))
