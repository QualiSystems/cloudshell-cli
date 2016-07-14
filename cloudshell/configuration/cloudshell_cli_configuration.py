from collections import OrderedDict

from cloudshell.cli.session.session_creator import SessionCreator
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.session_proxy import ReturnToPoolProxy
from cloudshell.cli.session.tcp_session import TCPSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.shell.core.context_utils import get_attribute_by_name_wrapper, get_resource_address, \
    get_decrypted_password_by_attribute_name_wrapper

"""Session types implemented in current package"""
CONNECTION_TYPE_SSH = 'ssh'
CONNECTION_TYPE_TELNET = 'telnet'
CONNECTION_TYPE_TCP = 'tcp'
CONNECTION_TYPE_AUTO = 'auto'

"""Connection map, defines SessionCreator objects which used for session creation"""
CONNECTION_MAP = OrderedDict()

"""Definition for SSH session"""
ssh_session = SessionCreator(SSHSession)
ssh_session.proxy = ReturnToPoolProxy
ssh_session.kwargs = {'username': get_attribute_by_name_wrapper('User'),
                      'password': get_decrypted_password_by_attribute_name_wrapper('Password'),
                      'host': get_resource_address}
CONNECTION_MAP[CONNECTION_TYPE_SSH] = ssh_session

"""Definition for TCP session"""
tcp_session = SessionCreator(TCPSession)
tcp_session.proxy = ReturnToPoolProxy
tcp_session.kwargs = {'host': get_resource_address}
CONNECTION_MAP[CONNECTION_TYPE_TCP] = tcp_session

"""Definition for Telnet session"""
telnet_session = SessionCreator(TelnetSession)
telnet_session.proxy = ReturnToPoolProxy
telnet_session.kwargs = {'username': get_attribute_by_name_wrapper('User'),
                         'password': get_decrypted_password_by_attribute_name_wrapper('Password'),
                         # 'password': get_attribute_by_name_wrapper('Password'),
                         'host': get_resource_address}
CONNECTION_MAP[CONNECTION_TYPE_TELNET] = telnet_session

"""Function or string that defines connection type"""
CONNECTION_TYPE = get_attribute_by_name_wrapper('CLI Connection Type')
DEFAULT_CONNECTION_TYPE = CONNECTION_TYPE_AUTO

"""Maximum number of sessions that can be created"""
DEFAULT_SESSION_POOL_SIZE = 1
SESSION_POOL_SIZE = get_attribute_by_name_wrapper('Sessions Concurrency Limit')

"""Max time waiting session from pool"""
POOL_TIMEOUT = 600

DEFAULT_PROMPT = r'.*[>$#]\s*$'
# PROMPT = DEFAULT_PROMPT
CONFIG_MODE_PROMPT = r'.*#\s*$'
ENTER_CONFIG_MODE_PROMPT_COMMAND = 'configure'
EXIT_CONFIG_MODE_PROMPT_COMMAND = 'exit'

"""Commit rollback commands"""
COMMIT_COMMAND = 'commit'
ROLLBACK_COMMAND = 'rollback'

EXPECTED_MAP = OrderedDict()
# ERROR_MAP = OrderedDict({r'.*':'ErrorError'})
ERROR_MAP = OrderedDict()

COMMAND_RETRIES = 10
