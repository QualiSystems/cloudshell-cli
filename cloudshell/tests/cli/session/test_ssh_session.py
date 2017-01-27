import socket
import threading
from StringIO import StringIO
from abc import abstractmethod
from time import sleep
from unittest import TestCase, skip

import paramiko
from paramiko import RSAKey

from cloudshell.cli.session.ssh_session import SSHSession
from mock import Mock, patch


class FakeDevice:
    def __init__(self):
        pass

    @abstractmethod
    def get_banner(self):
        """

        :return: str : the welcome banner of the fake device
        """
        pass

    @abstractmethod
    def do_command(self, command):
        """

        :param command: command to execute
        :return: (str, str, int) stdout, stderr, return code
        """
        pass


class DefaultFakeDevice(FakeDevice):
    NORMAL_PROMPT = '[prompt] $ # > '
    ENABLE_PROMPT = '[enable] $ # > '

    def __init__(self):
        FakeDevice.__init__(self)
        self.prompt = self.NORMAL_PROMPT

    def get_banner(self):
        """

        :return: str
        """
        return '--------------\nWelcome to the default fake device\n--------------\n%s' % self.prompt

    def do_command(self, command):
        """

        :param command: str : command to execute
        :return: (str, str, int) : stdout, stderr, return code
        """
        if command == 'enable':
            self.prompt = self.ENABLE_PROMPT
        if command == 'exit':
            self.prompt = self.NORMAL_PROMPT
        output = ''.join(['%s ' % s for s in command])  # c o m m a n d
        return '%s\noutput of "%s"\n%s' % (command, output, self.prompt), '', 0


class SFTPReceiver(paramiko.SFTPHandle):
    def __init__(self, buf, flags=0):
        super(SFTPReceiver, self).__init__(flags)
        self.buf = buf

    def write(self, offset, data):
        self.buf.write(data)
        return paramiko.SFTP_OK

    def close(self):
        super(SFTPReceiver, self).close()


class SFTPServerInterface(paramiko.SFTPServerInterface):
    def __init__(self, server, *largs, **kwargs):
        self.server = server
        self.channel = None

    def stat(self, path):
        rv = paramiko.SFTPAttributes()
        rv.st_size = len(self.server.filename2stringio[path].getvalue())
        return rv

    def chattr(self, path, attr):
        return paramiko.SFTP_OK

    def open(self, path, flags, attr):
        # print 'OPEN'
        buf = StringIO()
        self.server.filename2stringio[path] = buf
        return SFTPReceiver(buf)

    def session_started(self):
        # print 'session_started'
        super(SFTPServerInterface, self).session_started()

    def session_ended(self):
        # print 'session_ended'
        super(SFTPServerInterface, self).session_ended()
        # self.server.channels.remove(self.channel)
        # self.channel = None


class SFTPHandler(paramiko.SFTPServer):
    def __init__(self, channel, name, server, sftp_si=SFTPServerInterface, *largs, **kwargs):
        super(SFTPHandler, self).__init__(channel, name, server, SFTPServerInterface, *largs, **kwargs)
        self.server.channel = channel


class SSHServer(paramiko.ServerInterface):
    def __init__(self,
                 listen_addr='127.0.0.1',
                 port=0,
                 server_key_string=None,
                 user2key=None,
                 user2password=None,
                 fake_device=None,
                 enable_sftp=False,
                 enable_scp=False,
                 *largs, **kwargs):
        """

        :param listen_addr: str : which local IP to listen on, default 127.0.0.1
        :param port: int : listening port for the SSH server, or 0 to let the system choose; if 0 was used, check the .port field for the assigned port
        :param server_key_string: str : private key for the server's identity; leave blank to generate
        :param user2key: dict[str, PKey] : mapping from each username to the correct public or private PKey
        :param user2password: dict[str, str] : mapping from each username to the correct password
        :param fake_device: FakeDevice : an object that responds to commands
        :param enable_sftp: bool : whether to respond to SFTP requests
        :param enable_scp: bool : whether to respond to SCP requests
        :param largs:
        :param kwargs:
        """

        paramiko.ServerInterface.__init__(self)
        self.enable_sftp = enable_sftp
        self.enable_scp = enable_scp
        self.user2key = user2key or {}
        self.user2password = user2password or {}
        self.fake_device = fake_device or DefaultFakeDevice()
        self.server_key = RSAKey.from_private_key(StringIO(server_key_string)) if server_key_string else RSAKey.generate(2048)
        self.reads = {}
        self.filename2stringio = {}
        self.channelid2scpfilename = {}
        self.channelid2subsystem = {}
        self.channels = set()
        self.scpchannelid2command = {}
        self.channelid2event = {}

        self.listensock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listensock.bind((listen_addr, port))
        self.listensock.listen(5)
        self.port = self.listensock.getsockname()[1]

        t = threading.Thread(target=self.sockthread)
        t.setDaemon(True)
        t.start()

    def sockthread(self):
        while True:
            try:
                conn, addr = self.listensock.accept()
                if not conn:
                    return
            except:
                return

            self.transport = paramiko.Transport(conn)
            self.transport.add_server_key(self.server_key)
            if self.enable_sftp:
                self.transport.set_subsystem_handler('sftp', SFTPHandler)

            self.transport.start_server(server=self)

            t2 = threading.Thread(target=self.transportthread)
            t2.setDaemon(True)
            t2.start()

    def transportthread(self):
        # print 'starting transport thread'
        while True:
            ch = self.transport.accept()
            if ch is None:
                # print 'transport accept None channel'
                return
            # print 'transport accept channel %d' % ch.get_id()

            self.channels.add(ch)

    def scp_session_thread(self, channel):
        # print 'starting session thread %d' % channel.get_id()
        self.reads[channel.get_id()] = []
        buf = ''
        while True:
            b = channel.recv(1024)
            self.reads[channel.get_id()].append(b)
            if len(b) > 0:
                buf += b
            if buf.endswith('\n') or buf.endswith('\r') or buf.endswith('\x00'):
                if '\x00' not in buf:
                    buf = buf.strip()

                # print 'got:'
                # print buf
                if channel.get_id() not in self.channelid2scpfilename and buf.startswith('C'):
                    filename = buf.strip().split(' ')[2]
                    self.channelid2scpfilename[channel.get_id()] = filename
                    self.filename2stringio[filename] = StringIO()
                    channel.sendall('\x00')
                else:
                    filename = self.channelid2scpfilename[channel.get_id()]
                    self.filename2stringio[filename].write(buf.replace('\x00', ''))
                    if '\x00' in buf:
                        channel.sendall('\x00')
                buf = ''
            if len(b) == 0:
                # print 'closing channel %d on empty recv' % channel.get_id()
                # print self.filename2stringio
                channel.close()
                return

    def session_thread(self, channel):
        # print 'starting session thread %d' % channel.get_id()
        self.reads[channel.get_id()] = []
        channel.sendall(self.fake_device.get_banner())
        buf = ''
        while True:
            b = channel.recv(1024)
            self.reads[channel.get_id()].append(b)
            if len(b) > 0:
                buf += b
            if buf.endswith('\n') or buf.endswith('\r'):
                buf = buf.strip()
                o, e, _ = self.fake_device.do_command(buf)
                if o:
                    channel.sendall(o)
                if e:
                    channel.sendall(e)
                buf = ''
            if len(b) == 0:
                # print 'closing channel %d on empty recv' % channel.get_id()
                channel.close()
                return

    def stop(self):
        try:
            self.listensock.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.listensock.close()
        except:
            pass
        self.listensock = None

    def __del__(self):
        self.stop()

    def check_auth_publickey(self, username, key):
        if self.user2key.get(username) == key:
            return paramiko.AUTH_SUCCESSFUL
        else:
            return paramiko.AUTH_FAILED

    def check_channel_exec_request(self, channel, command):
        # print 'channel %d exec command %s' % (channel.get_id(), command)
        if command.startswith('scp'):
            if not self.enable_scp:
                return False
            self.scpchannelid2command[channel.get_id()] = command
            channel.sendall('\x00')
            t3 = threading.Thread(target=self.scp_session_thread, args=(channel,))
            t3.setDaemon(True)
            t3.start()
        else:
            o, e, ret = self.fake_device.do_command(command)
            if o:
                channel.sendall(o)
            if e:
                channel.sendall_stderr(e)
            channel.send_exit_status(ret)
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        # print 'pty request channel %d' % channel.get_id()
        return True

    def check_channel_env_request(self, channel, name, value):
        # print 'env request channel %d' % channel.get_id()
        return True

    def check_channel_shell_request(self, channel):
        # print 'shell request %d' % channel.get_id()
        t3 = threading.Thread(target=self.session_thread, args=(channel,))
        t3.setDaemon(True)
        t3.start()
        return True

    def check_auth_password(self, username, password):
        # print 'check auth'
        if self.user2password.get(username) == password:
            return paramiko.AUTH_SUCCESSFUL
        else:
            return paramiko.AUTH_FAILED

    def check_channel_subsystem_request(self, channel, name):
        # print 'subsystem request channel %d %s' % (channel.get_id(), name)
        return super(SSHServer, self).check_channel_subsystem_request(channel, name)

    def get_allowed_auths(self, username):
        if self.user2password:
            if self.user2key:
                return "password,publickey"
            else:
                return "password"
        else:
            if self.user2key:
                return "publickey"
            else:
                return ""

    def check_channel_request(self, kind, chanid):
        # print 'channel request kind="%s" channel %d' % (kind, chanid)
        return paramiko.OPEN_SUCCEEDED


class TestSshSession(TestCase):
    def setUp(self):
        self._username = 'user'
        self._password = 'pass'
        self._hostname = 'hostname'
        self._port = 22
        self._on_session_start = Mock()

    @patch('cloudshell.cli.session.ssh_session.ExpectSession')
    @patch('cloudshell.cli.session.ssh_session.ConnectionParams')
    def test_init_attributes(self, connection_params, expect_session):
        self._instance = SSHSession(self._hostname, self._username, self._password, port=self._port,
                                    on_session_start=self._on_session_start)
        mandatory_attributes = ['username', '_handler', '_current_channel', 'password', '_buffer_size']
        self.assertEqual(len(set(mandatory_attributes).difference(set(self._instance.__dict__.keys()))), 0)

    @patch('cloudshell.cli.session.ssh_session.ExpectSession')
    def test_eq(self, expect_session):
        self._instance = SSHSession(self._hostname, self._username, self._password, port=self._port,
                                    on_session_start=self._on_session_start)
        self.assertTrue(
            self._instance.__eq__(SSHSession(self._hostname, self._username, self._password, port=self._port,
                                             on_session_start=self._on_session_start)))
        self.assertFalse(
            self._instance.__eq__(SSHSession(self._hostname, 'incorrect_username', self._password, port=self._port,
                                             on_session_start=self._on_session_start)))
        self.assertFalse(
            self._instance.__eq__(SSHSession(self._hostname, self._username, 'incorrect_password', port=self._port,
                                             on_session_start=self._on_session_start)))


    def test_upload_sftp(self):
        server = SSHServer(user2password={'user0': 'password0'}, enable_sftp=True, enable_scp=False)
        self._instance = SSHSession('127.0.0.1',
                                    'user0', 'password0',
                                    port=server.port,
                                    on_session_start=self._on_session_start)
        self._instance.connect('>', logger=Mock())
        self._instance.upload_sftp(StringIO('klmno'), 'z.txt', 5, '0601')
        self.assertTrue(server.filename2stringio['z.txt'].getvalue() == 'klmno')

    def test_upload_scp(self):
        server = SSHServer(user2password={'user0': 'password0'}, enable_sftp=False, enable_scp=True)
        self._instance = SSHSession('127.0.0.1',
                                    'user0', 'password0',
                                    port=server.port,
                                    on_session_start=self._on_session_start)
        self._instance.connect('>', logger=Mock())
        self._instance.upload_scp(StringIO('abcde'), 'y.txt', 5, '0601')
        sleep(3)
        self.assertTrue(server.filename2stringio['y.txt'].getvalue() == 'abcde')

