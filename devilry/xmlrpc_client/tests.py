from tempfile import mkdtemp
from shutil import rmtree
import os
from ConfigParser import ConfigParser

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from devilry.xmlrpc.testhelpers import get_serverproxy, XmlRpcAssertsMixin
from devilry.core.testhelpers import create_from_path
from devilry.core.models import Delivery

from cookie_transport import CookieTransport, SafeCookieTransport
from command import Command
from utils import AssignmentSync, InfoFileDoesNotExistError, \
    InfoFileWrongTypeError, InfoFileMissingSectionError

import logging
logging.basicConfig(level=logging.DEBUG)


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


class TestAssignmentSyncBase(TestCase, XmlRpcAssertsMixin):
    fixtures = ['tests/xmlrpc_examiner/users',
            'tests/xmlrpc_examiner/core']

    def sync(self):
        return AssignmentSync(
                self.root,
                os.path.join(self.root, 'cookie.txt'),
                self.server, 'http://test')

    def setUp(self):
        self.client = Client()
        self.server = get_serverproxy(self.client, '/xmlrpc_examiner/')
        self.login(self.client, 'examiner1')
        self.root = mkdtemp('devilry-test')
        self.sync()
        self.examiner1 = User.objects.get(username='examiner1')
        self.student2 = User.objects.get(username='student2')

    def tearDown(self):
        self.logout(self.client)
        rmtree(self.root)


class TestAssignmentSync(TestAssignmentSyncBase):
    def setUp(self):
        super(TestAssignmentSync, self).setUp()
        self.infofile = os.path.join(self.root, 'inf1100.looong.oblig1',
                '.info')

    def test_sync(self):
        self.assertEquals(os.listdir(self.root), ['inf1100.looong.oblig1'])
        assignmentgroup = create_from_path(
                'ifi:inf1010.spring09.oblig1.student1')
        assignmentgroup.examiners.add(self.examiner1)
        assignmentgroup.save()
        self.sync()
        dircontent = os.listdir(self.root)
        dircontent.sort()
        self.assertEquals(dircontent,
                ['inf1010.spring09.oblig1', 'inf1100.looong.oblig1'])
        info = ConfigParser() # Sanity test of info-file
        info.read([self.infofile])
        self.assertEquals(
                info.get('info', 'path'), 'inf1100.looong.oblig1')
        self.assertEquals(info.get('info', 'id'), '1')

    def test_infofile(self):
        self.assertTrue(os.path.isfile(self.infofile))
        info = ConfigParser()
        info.read([self.infofile])
        self.assertEquals(
                info.get('info', 'path'), 'inf1100.looong.oblig1')
        self.assertEquals(info.get('info', 'id'), '1')
        self.assertEquals(info.get('info', 'short_name'), 'oblig1')
        self.assertEquals(
                info.get('info', 'long_name'), 'Obligatory assignment one')
        self.assertEquals(info.get('info', 'path'), 'inf1100.looong.oblig1')
        self.assertEquals(
                info.get('info', 'publishing_time'), '2010-06-05 00:31:42')

    def test_assignment_missing_infofile(self):
        infofile = os.path.join(self.root, 'inf1100.looong.oblig1',
                '.info')
        os.remove(infofile)
        self.assertRaises(InfoFileDoesNotExistError, self.sync)

    def test_assignment_infofile_missing_section(self):
        infofile = os.path.join(self.root, 'inf1100.looong.oblig1',
                '.info')
        i = open(infofile, 'rb').read().replace('[info]', '[somethingelse]')
        open(infofile, 'wb').write(i)
        self.assertRaises(InfoFileMissingSectionError, self.sync)

    def test_assignment_infofile_wrongtype(self):
        infofile = os.path.join(self.root, 'inf1100.looong.oblig1',
                '.info')
        i = open(infofile, 'rb').read().replace('type = Assignment',
                'type = somethingelse')
        open(infofile, 'wb').write(i)
        self.assertRaises(InfoFileWrongTypeError, self.sync)


class TestAssignmentGroupSync(TestAssignmentSyncBase):
    def setUp(self):
        super(TestAssignmentGroupSync, self).setUp()
        self.infofile = os.path.join(self.root, 'inf1100.looong.oblig1',
                'student2-student3', '.info')
        self.folder = os.path.join(self.root, 'inf1100.looong.oblig1')

    def test_sync(self):
        l = os.listdir(self.folder)
        l.sort()
        self.assertEquals(l, ['.info', 'student1', 'student2-student3'])

    def test_infofile(self):
        self.assertTrue(os.path.isfile(self.infofile))
        info = ConfigParser()
        info.read([self.infofile])
        self.assertEquals(info.get('info', 'id'), '2')
        self.assertEquals(info.get('info', 'name'), '')
        self.assertEquals(
                info.get('info', 'students'), 'student2, student3')
        self.assertEquals(
                info.get('info', 'number_of_deliveries'), '1')

    def test_namecrash(self):
        assignmentgroup = create_from_path(
                'uio.ifi:inf1100.looong.oblig1.student2,student3')
        assignmentgroup.examiners.add(self.examiner1)
        assignmentgroup.save()
        delivery = Delivery.begin(assignmentgroup, self.student2)
        delivery.finish()
        self.sync()
        dircontent = os.listdir(self.folder)
        dircontent.sort()
        self.assertEquals(dircontent,
            ['.info', 'student1', 'student2-student3.2',
            'student2-student3.%s' % assignmentgroup.id])

        # Make sure it works when id-based names are in the fs
        self.sync()
        dircontent = os.listdir(self.folder)
        dircontent.sort()
        self.assertEquals(dircontent,
            ['.info', 'student1', 'student2-student3.2',
            'student2-student3.%s' % assignmentgroup.id])
