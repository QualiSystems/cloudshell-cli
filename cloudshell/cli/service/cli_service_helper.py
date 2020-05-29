class SendCommandWithRetries(object):
    """
    Help to execute command with retries.

    If command execution raise an exception it helps
    to reconnect or create a new session from the list of
    defined sessions, optional.
    """

    MAX_RECREATE_RETRIES = 3
    MAX_RECONNECT_RETRIES = 0
    RECONNECT_TIMEOUT = 30

    def __init__(
        self,
        cli_configurator,
        command_mode,
        logger,
        recreate_retries=None,
        reconnect_retries=None,
        reconnect_timeout=None,
    ):
        """
        Init method.

        :param cloudshell.cli.configurator.CLIServiceConfigurator cli_configurator:
        :param cloudshell.cli.service.command_mode.CommandMode command_mode:
        :param logging.Logger logger:
        :param int recreate_retries:
        :param int reconnect_retries:
        :param int reconnect_timeout:
        """
        self.cli_configurator = cli_configurator
        self.command_mode = command_mode
        self._logger = logger
        self._recreate_retries = recreate_retries or self.MAX_RECREATE_RETRIES
        self._reconnect_retries = reconnect_retries or self.MAX_RECONNECT_RETRIES
        self._reconnect_timeout = reconnect_timeout or self.RECONNECT_TIMEOUT

    def _send_command_with_reconnect(self, cli_service, *args, **kwargs):
        """Send command with reconnect retries."""
        retry = 0
        while True:
            try:
                return cli_service.send_command(*args, **kwargs)
            except Exception:
                self._logger.exception("Reconnect retry {}".format(retry))
                if retry < self._reconnect_retries:
                    cli_service.reconnect(self._reconnect_timeout)
                    retry += 1
                else:
                    raise

    def send_command(self, *args, **kwargs):
        """Send command with retries on fail."""
        retry = 0
        while retry < self._recreate_retries:
            try:
                with self.cli_configurator.get_cli_service(
                    self.command_mode
                ) as cli_service:
                    self._send_command_with_reconnect(cli_service, *args, **kwargs)
            except Exception:
                self._logger.exception("Recreate retry {}".format(retry))
                retry += 1
        raise Exception("Max retries exceeded")
