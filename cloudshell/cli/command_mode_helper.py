from collections import OrderedDict

import re
from cloudshell.cli.command_mode import CommandMode, CommandModeException
from cloudshell.cli.node import NodeOperations
from cloudshell.cli.session.session import Session


class CommandModeHelper(NodeOperations):
    @staticmethod
    def determine_current_mode(session, command_mode, logger):
        """
        Determine current command mode
        :param session:
        :type session: Session
        :param command_mode
        :type command_mode: CommandMode
        :return: command_mode
        :rtype: CommandMode
        """

        defined_modes = CommandModeHelper.defined_modes_by_prompt(command_mode)
        prompts_re = r'|'.join(defined_modes.keys())
        try:
            result = session.probe_for_prompt(expected_string=prompts_re, logger=logger)
        except Exception as e:
            logger.debug(e.message)
            raise CommandModeException(CommandModeHelper.__class__.__name__,
                                       'Cannot determine current command mode, see logs for more details')

        for prompt, mode in defined_modes.iteritems():
            if re.search(prompt, result):
                return mode

    @staticmethod
    def defined_modes_by_prompt(command_mode):
        """
        Find all modes by relations and generate dict
        :return:
        :rtype: OrderedDict
        """

        def _get_child_nodes(command_node):
            return reduce(lambda x, y: x + _get_child_nodes(y), [command_node.child_nodes] + command_node.child_nodes)

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
        """
        Create specific command mode with relations
        :param command_mode_type:
        :param args:
        :param kwargs:
        :return:
        :rtype: dict
        """

        def _create_child_modes(instance, child_dict):
            instance_dict = {}
            for mode_type in child_dict:
                mode_instance = mode_type(*args, **kwargs)
                instance_dict[mode_type] = mode_instance
                mode_instance.add_parent_mode(instance)
                instance_dict[mode_type] = mode_instance
                instance_dict.update(_create_child_modes(mode_instance, child_dict[mode_type]))
            return instance_dict

        return _create_child_modes(None, CommandMode.RELATIONS_DICT)
