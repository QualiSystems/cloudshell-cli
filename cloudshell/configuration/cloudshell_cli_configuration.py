from collections import OrderedDict

from cloudshell.cli.connection_manager import SessionCreator
from cloudshell.cli.ssh_session import SSHSession
from cloudshell.cli.connection_manager import ReturnToPoolProxy
from cloudshell.shell.core.context.context_utils import get_attribute_by_name_wrapper
from cloudshell.shell.core.context.context_utils import get_resource_address
from cloudshell.cli.connection_manager import get_thread_session

"""Defines function for getting session, used in binding for session"""
# GET_SESSION = ConnectionManager.get_session
GET_SESSION = get_thread_session

"""Session types implemented in current package"""
CONNECTION_TYPE_SSH = 'ssh'
CONNECTION_TYPE_TELNET = 'telnet'
CONNECTION_TYPE_AUTO = 'auto'

"""Connection map, defines SessionCreator objects which used for session creation"""
CONNECTION_MAP = OrderedDict()

"""Definition for SSH session"""
ssh_session = SessionCreator(SSHSession)
ssh_session.proxy = ReturnToPoolProxy
ssh_session.kwargs = {'username': get_attribute_by_name_wrapper('User'),
                      'password': get_attribute_by_name_wrapper('Password'),
                      'host': get_resource_address}
CONNECTION_MAP[CONNECTION_TYPE_SSH] = ssh_session


# CONNECTION_MAP['tcp'] = SessionHelper(TCPSession)
# CONNECTION_MAP['tcp'].kwargs
# CONNECTION_MAP['console'] = SessionHelper(ConsoleSession,
#                                                    ['console_server_ip', 'console_server_user',
#                                                     'console_server_password', 'console_port'])
# CONNECTION_MAP['telnet'] = SessionHelper(TelnetSession)
# CONNECTION_MAP['ssh'] = SessionHelper(SSHSession)

# CONNECTION_MAP = {CONNECTION_TYPE_SSH: CONNECTION_MAP[CONNECTION_TYPE_SSH]}

"""Function or string that defines connection type"""
# CONNECTION_TYPE = get_attribute_wrapper('Connection Type')
CONNECTION_TYPE = CONNECTION_TYPE_AUTO

"""Maximum number of sessions that can be created"""
SESSION_POOL_SIZE = 1
"""Max time waiting session from pool"""
POOL_TIMEOUT = 60

DEFAULT_PROMPT = r'.*[>$#]\s*$'
# PROMPT = DEFAULT_PROMPT
CONFIG_MODE_PROMPT = r'.*#\s*$'
ERROR_LIST = []

EXPECTED_MAP = OrderedDict()
# ERROR_MAP = OrderedDict({r'.*':'ErrorError'})
ERROR_MAP = OrderedDict()

COMMAND_RETRIES = 10
