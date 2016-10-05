import re
from cloudshell.cli.command_mode import CommandMode, CommandModeException
from cloudshell.cli.node import NodeOperations
from cloudshell.cli.cli_operations import CliOperations


class CommandModeHelper(object):
    @staticmethod
    def change_session_mode(session, command_mode, logger):
        """
        Change session command mode
        :param session:
        :type session: CliOperations
        :param command_mode:
        :type command_mode: CommandMode
        :param logger:
        :type logger: Logger
        :return:
        """
        current_mode = CommandModeHelper.determine_current_mode(session, logger)
        steps = NodeOperations.calculate_route_steps(current_mode, command_mode)
        map(lambda x: x(session, logger), steps)
        session.command_mode = command_mode

    @staticmethod
    def determine_current_mode(session, logger):
        """
        Determine current command mode
        :param session:
        :type session: CliOperations
        :return: command_mode
        :rtype: CommandMode
        """

        prompts_re = r'|'.join(CommandMode.DEFINED_MODES.keys())
        try:
            result = session.send_command('', logger=logger, expected_string=prompts_re, timeout=5)
        except Exception as e:
            logger.debug(e.message)
            raise CommandModeException(CommandModeHelper.__class__.__name__,
                                       'Cannot determine current command mode, see logs for more details')

        for prompt, mode in CommandMode.DEFINED_MODES.iteritems():
            if re.search(prompt, result):
                return mode

