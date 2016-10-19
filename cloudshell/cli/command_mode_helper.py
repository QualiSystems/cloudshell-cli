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

        defined_modes = command_mode.defined_modes_by_prompt()
        prompts_re = r'|'.join(defined_modes.keys())
        try:
            result = session.hardware_expect('', expected_string=prompts_re, logger=logger)
        except Exception as e:
            logger.debug(e.message)
            raise CommandModeException(CommandModeHelper.__class__.__name__,
                                       'Cannot determine current command mode, see logs for more details')

        for prompt, mode in defined_modes.iteritems():
            if re.search(prompt, result):
                return mode
