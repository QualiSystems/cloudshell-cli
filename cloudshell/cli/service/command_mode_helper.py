from __future__ import annotations

from collections import OrderedDict
from functools import reduce
from typing import TYPE_CHECKING

from cloudshell.cli.service.command_mode import CommandMode, CommandModeException
from cloudshell.cli.service.node import NodeOperations

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.types import T_COMMAND_MODE_RELATIONS, T_SESSION


class CommandModeHelper(NodeOperations):
    @staticmethod
    def determine_current_mode(
        session: T_SESSION, command_mode: CommandMode, logger: Logger
    ) -> CommandMode:
        defined_modes = CommandModeHelper.defined_modes_by_prompt(command_mode)
        prompts_re = r"|".join(defined_modes.keys())
        try:
            result = session.probe_for_prompt(expected_string=prompts_re, logger=logger)
        except Exception:
            logger.exception("Cannot determine current command mode:")
            raise CommandModeException(
                "Cannot determine current command mode, see logs for more details"
            )

        for prompt, mode in defined_modes.items():
            if session.match_prompt(prompt, result, logger):
                return mode

    @staticmethod
    def defined_modes_by_prompt(command_mode: CommandMode) -> dict[str, CommandMode]:
        """Find all modes by relations and generate dict."""

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
    def create_command_mode(*args, **kwargs) -> T_COMMAND_MODE_RELATIONS:
        """Create specific command mode with relations."""

        def _create_child_modes(
            instance: CommandMode | None, child_dict: T_COMMAND_MODE_RELATIONS
        ) -> T_COMMAND_MODE_RELATIONS:
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
