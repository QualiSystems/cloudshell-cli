import logging
from collections import OrderedDict
from functools import reduce
from typing import TYPE_CHECKING, List

from cloudshell.cli.process.mode.node import NodeOperations
from cloudshell.cli.session.core.session import Session

if TYPE_CHECKING:
    from cloudshell.cli.process.command.processor import CommandProcessor
    from cloudshell.cli.process.mode.command_mode import CommandMode

logger = logging.getLogger(__name__)


class CommandModeHelper(NodeOperations):
    @staticmethod
    def determine_current_mode(session: "CommandProcessor", command_mode: "CommandMode") -> "CommandMode":
        """Determine current command mode."""
        for mode in CommandModeHelper.get_defined_modes(command_mode):
            if mode.session_within(session):
                return mode

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
    def defined_modes_by_prompt(command_mode):
        """Find all modes by relations and generate dict.

        :rtype: OrderedDict
        """

        # noqa
        def _get_child_nodes(command_node):
            return reduce(
                lambda x, y: x + _get_child_nodes(y),
                [command_node.child_nodes] + command_node.child_nodes,
            )

        node = command_mode
        while node.parent_node:
            node = node.parent_node
        root_node = node

        node_list = [root_node] + _get_child_nodes(root_node)

        modes_dict = OrderedDict()
        for mode in node_list:
            modes_dict[mode.prompt] = mode
        return modes_dict

    @staticmethod
    def create_command_mode(*args, **kwargs):
        """Create specific command mode with relations.

        :rtype: dict
        """

        # noqa
        def _create_child_modes(instance, child_dict):
            instance_dict = {}
            for mode_type in child_dict:
                mode_instance = mode_type(*args, **kwargs)
                instance_dict[mode_type] = mode_instance
                mode_instance.add_parent_mode(instance)
                instance_dict[mode_type] = mode_instance
                instance_dict.update(
                    _create_child_modes(mode_instance, child_dict[mode_type])
                )
            return instance_dict

        return _create_child_modes(None, CommandMode.RELATIONS_DICT)

    @staticmethod
    def change_mode(command_processor: "CommandProcessor", current_mode: "CommandMode",
                    requested_mode: "CommandMode") -> None:
        """Change command mode."""
        steps = CommandModeHelper.calculate_route_steps(
            current_mode, requested_mode
        )
        list(map(lambda x: x(command_processor), steps))
