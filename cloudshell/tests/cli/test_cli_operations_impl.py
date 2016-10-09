import unittest

from mock import MagicMock
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.cli import Cli
from cloudshell.cli.cli_operations_impl import CliOperationsImpl as CliOperations
from cloudshell.cli.session_pool_manager import SessionPoolManager

CLI_MODE = CommandMode(r'%\s*$', '', 'exit', default_actions=lambda s: s.send_command('echo 123'))
DEFAULT_MODE = CommandMode(r'>\s*$', 'cli', 'exit', parent_mode=CLI_MODE,
                           default_actions=lambda s: s.send_command('set cli screen-length 0'))
CONFIG_MODE = CommandMode(r'#\s*$', 'configure', 'exit', parent_mode=DEFAULT_MODE)


class CLITest(unittest.TestCase):

    def set_attributes(self):
        self.session = MagicMock()
        self._logger = MagicMock()
        self._cli_operations =  MagicMock()
        self._command_mode =  MagicMock()
        self.logger =  MagicMock()
        self._previous_mode = None
        self._session_pool = SessionPoolManager()
        self._connection_attrs = {
        'host': '192.168.28.150',
        'username': 'root',
        'password': 'Juniper'}


    def test_enter_mode(self):
        self.set_attributes()
        res = '''
        show interfaces
        ge-0/0/0 {
            disable;
            unit 0 {
                family ethernet-switching {
                    port-mode access;
                    vlan {
                        members vlan-2;
                    }
                }
            }
        }
        ge-0/0/1 {
            unit 0 {
                family ethernet-switching {
                    port-mode access;
                }
            }
        }
        ge-0/0/2 {
            disable;
            unit 0 {
                family ethernet-switching {
                    port-mode access;
                }
            }
        }
        ge-0/0/3 {
            unit 0 {
                family inet {
                    address 192.168.28.150/24;
                }
            }
        }
        ge-0/0/4 {
            disable;
            gigether-options {
                802.3ad ae0;
            }
        }
        ge-0/0/5 {
            unit 0 {
                family ethernet-switching {
                    port-mode access;
                }
            }
        }
        ge-0/0/6 {
            disable;
            unit 0 {
                family ethernet-switching {
                    port-mode trunk;
                }
            }
        }
        ge-0/0/7 {
            unit 0 {
                family ethernet-switching {
                    port-mode access;
                }
            }
        }
        ae0 {
            aggregated-ether-options {
                lacp {
                    active;
                }
            }
            unit 0 {
                family ethernet-switching {
                    port-mode access;
                }
            }
        }
        vlan {
            unit 0 {
                family inet {
                    address 192.168.1.1/24;
                }
            }
            unit 40 {
                family inet {
                    address 10.0.0.10/24;
                }
            }
            unit 41 {
                family inet {
                    address 192.168.41.250/24;
                }
            }
        }

        [edit]
        root#
        '''
        cli = Cli(logger=self.logger)

        prompts_re = CommandMode.modes_pattern()
        #session = SSHSession(host='192.168.28.150', username='root', password='Juniper',logger=self._logger, prompt=prompts_re)
        #session.connect(prompts_re, self._logger)
        session = self._session_pool.get_session(logger=self._logger, prompt=prompts_re,
                                                 session_type=SSHSession,
                                                 connection_attrs=self._connection_attrs)

        self._cli_operations = CliOperations(session, self._command_mode, self._logger)

        config = self._cli_operations.enter_mode(CONFIG_MODE)
        out = config.send_command('show interfaces')
        self.assertEqual(out, res)




def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CLITest))
    return suite

if __name__ == '__main__':
    unittest.main()