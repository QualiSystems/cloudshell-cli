import re

from cloudshell.networking.cli_handler_impl import CliHandlerImpl
from cloudshell.shell.standards.core import get_attribute_by_name

from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.command_mode_helper import CommandModeHelper


class EnableCommandMode(CommandMode):
    PROMPT = r"(?:(?!\)).)#\s*$"
    ENTER_COMMAND = "enable"
    EXIT_COMMAND = ""

    def __init__(self, context):
        """Initialize Enable command mode - default command mode for Cisco Shells."""
        self._context = context

        CommandMode.__init__(
            self,
            EnableCommandMode.PROMPT,
            EnableCommandMode.ENTER_COMMAND,
            EnableCommandMode.EXIT_COMMAND,
        )


class DefaultCommandMode(CommandMode):
    PROMPT = r">\s*$"
    ENTER_COMMAND = ""
    EXIT_COMMAND = ""

    def __init__(self, context):
        """Initialize Default command mode.

        Only for cases when session started not in enable mode
        """
        self._context = context
        CommandMode.__init__(
            self,
            DefaultCommandMode.PROMPT,
            DefaultCommandMode.ENTER_COMMAND,
            DefaultCommandMode.EXIT_COMMAND,
        )


class ConfigCommandMode(CommandMode):
    PROMPT = r"\(config.*\)#\s*$"
    ENTER_COMMAND = "configure terminal"
    EXIT_COMMAND = "exit"

    def __init__(self, context):
        """Initialize Config command mode."""
        exit_action_map = {
            self.PROMPT: lambda session, logger: session.send_line("exit", logger)
        }
        CommandMode.__init__(
            self,
            ConfigCommandMode.PROMPT,
            ConfigCommandMode.ENTER_COMMAND,
            ConfigCommandMode.EXIT_COMMAND,
            exit_action_map=exit_action_map,
        )


CommandMode.RELATIONS_DICT = {
    DefaultCommandMode: {EnableCommandMode: {ConfigCommandMode: {}}}
}


class SwitchCliHandler(CliHandlerImpl):
    def __init__(self, cli, context, logger):
        super(SwitchCliHandler, self).__init__(cli, context, logger, None)
        modes = CommandModeHelper.create_command_mode(context)
        self.default_mode = modes[DefaultCommandMode]
        self.enable_mode = modes[EnableCommandMode]
        self.config_mode = modes[ConfigCommandMode]

    @property
    def username(self):
        return get_attribute_by_name("User", self._context)

    @property
    def password(self):
        password = get_attribute_by_name(
            attribute_name="Password", context=self._context
        )
        return password

    def on_session_start(self, session, logger):
        """Send default commands to configure/clear session outputs."""
        self.enter_enable_mode(session=session, logger=logger)
        session.hardware_expect("terminal length 0", EnableCommandMode.PROMPT, logger)
        session.hardware_expect("terminal width 300", EnableCommandMode.PROMPT, logger)
        self._enter_config_mode(session, logger)
        session.hardware_expect("no logging console", ConfigCommandMode.PROMPT, logger)
        session.hardware_expect("exit", EnableCommandMode.PROMPT, logger)

    def enter_enable_mode(self, session, logger):

        enable_password = get_attribute_by_name(
            attribute_name="Enable Password", context=self._context
        )
        expect_map = {
            "[Pp]assword": lambda session, logger: session.send_line(
                enable_password, logger
            )
        }
        session.hardware_expect(
            "enable", EnableCommandMode.PROMPT, action_map=expect_map, logger=logger
        )
        result = session.hardware_expect(
            "",
            "{0}|{1}".format(DefaultCommandMode.PROMPT, EnableCommandMode.PROMPT),
            logger,
        )
        if not re.search(EnableCommandMode.PROMPT, result):
            raise Exception("enter_enable_mode", "Enable password is incorrect")

    def _enter_config_mode(self, session, logger):
        error_message = "Failed to enter config mode, please check logs, for details"
        output = session.hardware_expect(
            ConfigCommandMode.ENTER_COMMAND,
            "{0}|{1}".format(ConfigCommandMode.PROMPT, EnableCommandMode.PROMPT),
            logger,
        )
        if not re.search(ConfigCommandMode.PROMPT, output):
            raise Exception("_enter_config_mode", error_message)
