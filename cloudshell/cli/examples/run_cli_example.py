from threading import Thread

from cloudshell.cli.cli import Cli
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session_pool_manager import SessionPoolManager
from cloudshell.core.logger.qs_logger import get_qs_logger


class CliCommandMode(CommandMode):
    PROMPT = r'%\s*$'
    ENTER_COMMAND = ''
    EXIT_COMMAND = 'exit'

    def __init__(self, context):
        self._context = context
        CommandMode.__init__(self, CliCommandMode.PROMPT, CliCommandMode.ENTER_COMMAND,
                             CliCommandMode.EXIT_COMMAND, enter_action_map=self.enter_action_map(),
                             exit_action_map=self.exit_action_map(), enter_error_map=self.enter_error_map(),
                             exit_error_map=self.exit_error_map())

    def enter_actions(self, cli_operations):
        pass

    def enter_action_map(self):
        return {r'dfsad': lambda dd: dd.send(self._context)}

    def enter_error_map(self):
        return {}

    def exit_action_map(self):
        return {}

    def exit_error_map(self):
        return {}


class DefaultCommandMode(CommandMode):
    PROMPT = r'%\s*$|>\s*$'
    ENTER_COMMAND = 'cli'
    EXIT_COMMAND = 'exit'

    def __init__(self, context):
        self._context = context
        CommandMode.__init__(self, DefaultCommandMode.PROMPT,
                             DefaultCommandMode.ENTER_COMMAND,
                             DefaultCommandMode.EXIT_COMMAND)

    def enter_actions(self, cli_operations):
        cli_operations.send_command('', action_map={r'%\s*$': lambda session, logger: session.send_line('cli', logger)})
        cli_operations.send_command('set cli screen-length 0')


class ConfigCommandMode(CommandMode):
    PROMPT = r'#\s*$'
    ENTER_COMMAND = 'configure'
    EXIT_COMMAND = 'exit'

    def __init__(self, context):
        CommandMode.__init__(self, ConfigCommandMode.PROMPT,
                             ConfigCommandMode.ENTER_COMMAND,
                             ConfigCommandMode.EXIT_COMMAND)

    def default_actions(self, cli_operations):
        pass

    def enter_actions(self, cli_operations):
        pass


CommandMode.RELATIONS_DICT = {
    DefaultCommandMode: {
        ConfigCommandMode: {}
    }
}

LOGGER = get_qs_logger()


def do_action(cli, session_type, mode, attrs):
    # session_type = SSHSession

    with cli.get_session(session_type, attrs, mode, LOGGER, ) as default_session:
        # out = default_session.send_command('show version', error_map={'srx220h-poe': 'big error'})
        out = default_session.send_command('show version')
        print(out)
        # config_command_mode = ConfigCommandMode(context)
        # config_command_mode.add_parent_mode(mode)
        # with default_session.enter_mode(config_command_mode) as config_session:
        #     out = config_session.send_command('show interfaces')
        #     print(out)
        #     out = config_session.send_command('show interfaces', logger=cli.logger)
        #     print(out)


class DefaultActions():
    def __init__(self, context):
        self._context = context

    def actions(self, session, logger):
        out = session.hardware_expect('echo ' + self._context.resource.name, DefaultCommandMode.PROMPT,
                                      logger,
                                      action_map={r'%\s*$': lambda session, logger: session.send_line('cli', logger)})
        # session.hardware_expect(DefaultCommandMode.ENTER_COMMAND, DefaultCommandMode.PROMPT, logger)
        # session.hardware_expect(ConfigCommandMode.ENTER_COMMAND, ConfigCommandMode.PROMPT, logger, action_list={})


if __name__ == '__main__':
    pool = SessionPoolManager(max_pool_size=1)
    cli = Cli(session_pool=pool)

    context = type('context', (object,), {'resource': type('resource', (object,), {'name': 'test name'})})


    # def default_actions(session, logger):
    #     out = ''
    #     cli_prompt = r'%\s*$'
    #     out = session.hardware_expect('echo ' + context.resource.name, cli_prompt + '|' + DefaultCommandMode.PROMPT,
    #                                   logger,
    #                                   action_map={r'%\s*$': lambda session: session.send_line('cli', logger)})
    #     # session.hardware_expect(DefaultCommandMode.ENTER_COMMAND, DefaultCommandMode.PROMPT, logger)
    #     # session.hardware_expect(ConfigCommandMode.ENTER_COMMAND, ConfigCommandMode.PROMPT, logger, action_list={})
    #     return out


    connection_attrs = {
        'host': '192.168.28.150',
        'username': 'root',
        'password': 'Juniper',
        'default_actions': DefaultActions(context).actions
    }

    connection_attrs1 = {
        'host': '192.168.28.150',
        'username': 'root',
        'password': 'Juniper',
        'default_actions': DefaultActions(context).actions
    }

    # session_types = [TelnetSession, SSHSession]
    session_types = SSHSession

    '''
    if context.session_type in session_types:
        session_type = session_types.get(context_session_type)
    else:
        session_type = session_types.values()
    '''
    # auto_session = [SSHSession, TelnetSession]
    # do_action(cli, session_types, DEFAULT_MODE, connection_attrs)

    # mode_template = CommandModeTemplate(context)

    # Thread(target=do_action, args=(cli, SSHSession, mode_template.config_mode(), connection_attrs)).start()
    # CommandModeFactory.connect_command_mode_types()
    # dd = DefaultActions(context)
    # connection_attrs['default_actions'] = dd.actions
    mode = CommandModeHelper.create_command_mode(DefaultCommandMode, context)
    Thread(target=do_action, args=(cli, session_types, mode, connection_attrs)).start()

    # del connection_attrs['default_actions']
    # gg = DefaultActions(context)
    # connection_attrs['default_actions'] = gg.actions
    mode = CommandModeHelper.create_command_mode(DefaultCommandMode, context)
    Thread(target=do_action, args=(cli, session_types, mode, connection_attrs1)).start()
    # Thread(target=do_action, args=(cli, DEFAULT_MODE)).start()

    # config_vlan_mode = CommandMode(r'vlan#/s*$', 'config vlan', 'exit')
    #
    # with config_session.enter_mode(config_vlan_mode) as config_vlan_session:
    #     config_vlan_session.send_command('command')
    #
    # config_session.send_command('do th..')
