import re
from cloudshell.cli.command_mode import CommandMode, CommandModeException
from cloudshell.cli.node import NodeOperations
from cloudshell.cli.session.session import Session


class CommandModeHelper(NodeOperations):
    @staticmethod
    def determine_current_mode(session, logger):
        """
        Determine current command mode
        :param session:
        :type session: Session
        :return: command_mode
        :rtype: CommandMode
        """

        prompts_re = CommandMode.modes_pattern()
        try:
            result = session.hardware_expect('', expected_string=prompts_re, logger=logger)
        except Exception as e:
            logger.debug(e.message)
            raise CommandModeException(CommandModeHelper.__class__.__name__,
                                       'Cannot determine current command mode, see logs for more details')

        for prompt, mode in CommandMode.DEFINED_MODES.iteritems():
            if re.search(prompt, result):
                return mode
