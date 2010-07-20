from tempfile import mkdtemp
from shutil import rmtree
import os
from ConfigParser import ConfigParser

from django.test import TestCase
#from django.test.client import Client

#from devilry.xmlrpc.testhelpers import get_serverproxy, XmlRpcAssertsMixin
from utils import Command


#class TestXmlRpc(TestCase, XmlRpcAssertsMixin):
    #fixtures = ['tests/xmlrpc_examiner/users',
            #'tests/xmlrpc_examiner/core']


class TestCommand(TestCase):
    def setUp(self):
        self.root = mkdtemp('devilry-test')
        self.devilrydir = os.path.realpath(
                os.path.join(self.root, '.devilry'))
        self.oldcwd = os.getcwd()
        os.chdir(self.root)
        os.mkdir(self.devilrydir)
        self.cmd = Command()

    def tearDown(self):
        os.chdir(self.oldcwd)
        rmtree(self.root)

    def test_config(self):
        self.assertEquals(self.devilrydir,
                os.path.realpath(self.cmd.find_configdir()))
        self.assertEquals(self.devilrydir,
                os.path.realpath(self.cmd.get_configdir()))
        self.cmd.set_config('hello', 'world')
        self.assertEquals('world', self.cmd.get_config('hello'))
        self.cmd.set_config('url', 'http://test')
        self.assertEquals('world', self.cmd.get_config('hello'))
        self.cmd.write_config()
        cfgfile = os.path.join(self.devilrydir, 'config.cfg')
        cfg = ConfigParser()
        cfg.read([cfgfile])
        self.assertEquals(cfg.get('settings', 'hello'), 'world')

    def test_split_relpath(self):
        p = Command.split_relpath('/home/example/devilry',
            '/home/example/devilry/hello/world')
        self.assertEquals(p, ['hello', 'world'])
