from tempfile import mkdtemp
from shutil import rmtree
import os
from ConfigParser import ConfigParser

from django.test import TestCase
from django.test.client import Client

from devilry.xmlrpc.testhelpers import get_serverproxy, XmlRpcAssertsMixin
from cookie_transport import CookieTransport, SafeCookieTransport
from command import Command
from utils import AssignmentSync


class TestCommand(TestCase):
    def setUp(self):
        self.root = mkdtemp(prefix='devilry-test-')
        self.configdir = os.path.realpath(
                os.path.join(self.root, '.devilry'))
        self.oldcwd = os.getcwd()
        os.chdir(self.root)
        os.mkdir(self.configdir)

        self.ob1dir = os.path.join(self.configdir, 'ifi.inf1100', 'oblig1')
        os.makedirs(self.ob1dir)
        open(os.path.join(self.ob1dir, '.assignment-id'), 'w').write('20')

        class TestCommand(Command):
            urlpath = '/xmlrpc/'
        self.cmd = TestCommand()

    def tearDown(self):
        os.chdir(self.oldcwd)
        rmtree(self.root)


    def test_get_rootdir(self):
        self.assertTrue(os.path.samefile(self.root,
            self.cmd.get_rootdir()))

    def test_config(self):
        self.assertTrue(os.path.samefile(self.configdir,
            self.cmd.get_configdir()))
        self.cmd.set_config('hello', 'world')
        self.assertEquals('world', self.cmd.get_config('hello'))
        self.cmd.set_config('url', 'http://test')
        self.assertEquals('world', self.cmd.get_config('hello'))
        self.cmd.write_config()
        cfgfile = os.path.join(self.configdir, 'config.cfg')
        cfg = ConfigParser()
        cfg.read([cfgfile])
        self.assertEquals(cfg.get('settings', 'hello'), 'world')

    def test_get_id_from_path(self):
        self.assertEquals(20,
                self.cmd.get_id_from_path(self.ob1dir, '.assignment-id'))

    def test_determine_id(self):
        self.assertEquals(10,
                self.cmd.determine_id('10', '.assignment-id'))
        self.assertEquals(20,
                self.cmd.determine_id(self.ob1dir, '.assignment-id'))

    def test_get_cookiepath(self):
        self.assertEquals(os.path.join(self.configdir, 'cookies.txt'),
                self.cmd.get_cookiepath())

    def test_get_serverproxy(self):
        self.cmd.set_config('url', 'http://test')
        serverproxy = self.cmd.get_serverproxy()._ServerProxy__transport
        self.assertTrue(isinstance(serverproxy, CookieTransport))
        self.cmd.set_config('url', 'https://test')
        serverproxy = self.cmd.get_serverproxy()._ServerProxy__transport
        self.assertTrue(isinstance(serverproxy, SafeCookieTransport))


class TestAssignmentSync(TestCase, XmlRpcAssertsMixin):
    fixtures = ['tests/xmlrpc_examiner/users',
            'tests/xmlrpc_examiner/core']

    def setUp(self):
        self.client = Client()
        self.server = get_serverproxy(self.client, '/xmlrpc_examiner/')
        self.login(self.client, 'examiner1')
        self.root = mkdtemp('devilry-test')
        self.atw = AssignmentSync(
                self.root,
                os.path.join(self.root, 'cookie.txt'),
                self.server, '')

    def test_it(self):
        pass

    def tearDown(self):
        self.server.logout()
        rmtree(self.root)
