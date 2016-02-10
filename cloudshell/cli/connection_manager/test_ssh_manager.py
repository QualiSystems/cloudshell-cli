import unittest

from qualipy.common.libs.connection_manager.ssh_manager import SSHManager
from qualipy.common.libs import qs_logger

def setUpModule():
    print 'SSH Manager unittest start!'

def tearDownModule():
    print '\nSSH Manager unittest end!'

class TestSSHManager(unittest.TestCase):
    @staticmethod
    def setUpClass():
        print 'SSH Test start'

    @staticmethod
    def tearDownClass():
        print '\nSSH Test end'

    def setUp(self):
        host = '127.0.0.1'
        port = 22

        user = 'admin'
        passwd = 'admin'

        logger = qs_logger.getQSLogger(handler_name='test')

        self._ssh = SSHManager(user, passwd, host, port, timeout = 600, logger = logger)
        print self._ssh.connect('[#$]{1}')
        print self._ssh.sendCommand('scope snmp', '[#$]{1}')
        print self._ssh.sendCommand('delete-virtual-cdrive', '-->')
        print self._ssh.sendCommand('yesss', '[#$]{1}')
        print self._ssh.sendCommand('top', '[#$]{1}')
        print self._ssh.sendCommand('scope snmp', '[#$]{1}')
        print self._ssh.sendCommand('scope snmp', '[#$]{1}')

    def tearDown(self):
        self._ssh.disconnect()

    def testSSHConnection(self):
        channel = self._ssh._current_channel
        self.assertNotEqual(channel, None)

    @unittest.skip('')
    def test_sendData(self):
        print self._ssh.sendCommand('exit', '')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSSHManager))

    return suite

if (__name__ == '__main__'):
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True: # raised by sys.exit(True) when tests failed
            pass