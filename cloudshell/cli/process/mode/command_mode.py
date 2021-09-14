from typing import TYPE_CHECKING, Optional

from cloudshell.cli.process.mode.node import Node

if TYPE_CHECKING:
    from cloudshell.cli.session.prompt.prompt import Prompt
    from cloudshell.cli.process.command.entities import Command
    from cloudshell.cli.process.command.processor import CommandProcessor


class CommandMode(Node):
    """Class describes our prompt and implement enter and exit command functions."""

    def __init__(
            self,
            prompt: Optional["Prompt"],
            enter_command: Optional["Command"] = None,
            exit_command: Optional["Command"] = None,
            parent_mode: Optional["CommandMode"] = None,
    ):
        """Initialize Command Mode."""

        super(CommandMode, self).__init__()
        self._prompt = prompt
        self._enter_command = enter_command
        self._exit_command = exit_command

        if parent_mode:
            self._add_parent_mode(parent_mode)

    @property
    def prompt(self) -> "Prompt":
        return self._prompt

    def _add_parent_mode(self, mode: Node) -> None:
        if mode:
            mode.add_child_node(self)

    def step_up(self, command_processor: "CommandProcessor") -> None:
        """Enter command mode."""
        prompt = command_processor.switch_prompt(self._enter_command)
        # if self.session_within(self):
        #     raise CommandModeException("Cannot match prompts")
        self.enter_actions(command_processor)
        # self.mode_actions(command_processor)

    def step_down(self, command_processor: "CommandProcessor") -> None:
        """Exit from command mode."""
        prompt = command_processor.switch_prompt(self._exit_command)
        # if self.parent_node.prompt != prompt:
        #     raise CommandModeException("Cannot match prompts")

    def session_within(self, command_processor: "CommandProcessor"):
        """Check if session within the mode"""
        return command_processor.session.get_prompt() == self.prompt

    def enter_actions(self, command_processor: "CommandProcessor"):
        pass
