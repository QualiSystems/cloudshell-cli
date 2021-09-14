import logging
from functools import reduce
from typing import TYPE_CHECKING, List

from cloudshell.cli.process.mode.exception import CommandModeException
from cloudshell.cli.process.mode.node import NodeOperations

if TYPE_CHECKING:
    from cloudshell.cli.process.command.processor import CommandProcessor
    from cloudshell.cli.process.mode.command_mode import CommandMode

logger = logging.getLogger(__name__)


class CommandModeHelper(NodeOperations):
    @staticmethod
    def determine_current_mode(command_processor: "CommandProcessor", command_mode: "CommandMode") -> "CommandMode":
        """Determine current command mode."""
        for mode in CommandModeHelper.get_defined_modes(command_mode):
            if mode.session_within(command_processor):
                return mode
        raise CommandModeException("Cannot associate session with command mode.")

    @staticmethod
    def get_defined_modes(command_mode: "CommandMode") -> List["CommandMode"]:
        """Find all modes by relations and generate list."""

        # noqa # todo rewrite to use generator
        def _get_child_nodes(command_node):
            return reduce(
                lambda x, y: x + _get_child_nodes(y),
                [command_node.child_nodes] + command_node.child_nodes,
            )

        node = command_mode
        while node.parent_node:
            node = node.parent_node
        root_node = node

        return [root_node] + _get_child_nodes(root_node)

    @staticmethod
    def change_mode(command_processor: "CommandProcessor", current_mode: "CommandMode",
                    requested_mode: "CommandMode") -> None:
        """Change command mode."""
        steps = CommandModeHelper.calculate_route_steps(
            current_mode, requested_mode
        )
        list(map(lambda x: x(command_processor), steps))
