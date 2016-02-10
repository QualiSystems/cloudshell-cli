__author__ = 'g8y3e'

import unittest

from qualipy.common.libs.connection_manager.telnet_manager import TelnetManager

def setUpModule():
    print 'SSH Manager unittest start!'

def tearDownModule():
    print '\nSSH Manager unittest end!'

class TestTelnetManager(unittest.TestCase):
    @staticmethod
    def setUpClass():
        print 'SSH Test start'

    @staticmethod
    def tearDownClass():
        print '\nSSH Test end'

    def setUp(self):
        username = 'val'
        password = '123456'
        host = '172.29.128.6'
        port = 23

        self._ssh = TelnetManager(username, password, host, port, timeout = 10)

        self._ssh.connect('[#$]{1}')
        print self._ssh.sendCommand('cd /lib', '[#$]{1}')
        print self._ssh.sendCommand('ls', '[#$]{1}')

    def tearDown(self):
        self._ssh.disconnect()

    def testSendData(self):
        data = self._ssh.sendCommand('cd /', '[#$]{1}')
        self.assertEqual(data[-1:], '$')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTelnetManager))

    return suite

if (__name__ == '__main__'):
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True: # raised by sys.exit(True) when tests failed
            pass