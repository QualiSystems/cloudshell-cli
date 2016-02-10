__author__ = 'yar'

# from qualipy.common.libs.connection_manager import ConnectionManager
# from qualipy.common.libs.ssh_manager import SSHManager
# from qualipy.common.libs.telnet_manager import TelnetManager
# from qualipy.common.libs import qs_logger
import paramiko


# ConnectionManager.CONNECTION_SETTINGS['telnet']['user']='test'
# ConnectionManager.CONNECTION_SETTINGS['telnet']['password']='test'
# ConnectionManager.CONNECTION_SETTINGS['telnet']['host']='test.com'
#
# cm = ConnectionManager(ssh_host='test.com', ssh_port=22, ssh_user='test_user', host='localhost', user='yar', password='12345', ssh_password='test_password', console_user='nnnd')
# #
# print(ConnectionManager.CONNECTION_SETTINGS)
# conn = cm.getConnection()
# if conn:
#     conn.sendCommand('ls')

# re_str='>|#|\(config.*\)#|Password:'
#
# # ssh = SSHManager('ini', '123456', '172.29.128.100', logger=qs_logger.getQSLogger())
# ssh = TelnetManager('ini', '123456', '172.29.128.100', logger=qs_logger.getQSLogger())
# ssh.connect(re_str)
# print(ssh.sendCommand('show version', re_str))
# print(ssh.sendCommand('enable', re_str))
# print(ssh.sendCommand('PASSWD', re_str))
# print(ssh.sendCommand('show version', re_str))
host = '10.11.169.187'
user = 'admin'
password = '@Vantage123'

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
connection = client.connect(host, 22, user, password, timeout=30, banner_timeout=30)
client.exec_command('show version')
client.exec_command('exit')
client.close()
