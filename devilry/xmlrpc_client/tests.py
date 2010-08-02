from tempfile import mkdtemp
from shutil import rmtree
import os
from ConfigParser import ConfigParser, NoOptionError
from datetime import datetime
from StringIO import StringIO
import logging

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from devilry.xmlrpc.testhelpers import get_serverproxy, XmlRpcAssertsMixin
from devilry.core.testhelpers import create_from_path
import devilry.core.models

from cookie_transport import CookieTransport, SafeCookieTransport
from assignmenttree import AssignmentSync, Info, join_dirname_id
import cli
import examinercmd


log = logging.getLogger('devilry')


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

        class TestCommand(cli.Command):
            urlpath = '/xmlrpc/'
        self.cmd = TestCommand()

    def tearDown(self):
        os.chdir(self.oldcwd)
        rmtree(self.root)

    def test_find_rootdir(self):
        self.assertTrue(os.path.samefile(self.root,
            self.cmd.find_rootdir()))

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
        self.root = mkdtemp(prefix='devilry-test')
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
                '.overwriteable-info')

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
                '.overwriteable-info')
        os.remove(infofile)
        self.assertRaises(Info.FileDoesNotExistError, self.sync)

    def test_assignment_infofile_missing_section(self):
        infofile = os.path.join(self.root, 'inf1100.looong.oblig1',
                '.overwriteable-info')
        i = open(infofile, 'rb').read().replace('[info]', '[somethingelse]')
        open(infofile, 'wb').write(i)
        self.assertRaises(Info.FileMissingSectionError, self.sync)

    def test_assignment_infofile_wrongtype(self):
        infofile = os.path.join(self.root, 'inf1100.looong.oblig1',
                '.overwriteable-info')
        i = open(infofile, 'rb').read().replace('type = Assignment',
                'type = somethingelse')
        open(infofile, 'wb').write(i)
        self.assertRaises(Info.FileWrongTypeError, self.sync)


class TestAssignmentGroupSync(TestAssignmentSyncBase):
    def setUp(self):
        super(TestAssignmentGroupSync, self).setUp()
        self.infofile = os.path.join(self.root, 'inf1100.looong.oblig1',
                'student2-student3', '.overwriteable-info')
        self.folder = os.path.join(self.root, 'inf1100.looong.oblig1')

    def test_sync(self):
        l = os.listdir(self.folder)
        l.sort()
        self.assertEquals(l, ['.overwriteable-info', 'student1', 'student2-student3'])

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
        delivery = devilry.core.models.Delivery.begin(assignmentgroup, self.student2)
        delivery.finish()
        self.sync()
        dircontent = os.listdir(self.folder)
        dircontent.sort()
        self.assertEquals(dircontent,
            ['.overwriteable-info', 'student1', 'student2-student3+2',
            join_dirname_id('student2-student3', assignmentgroup.id)])

        # Make sure it works when id-based names are in the fs
        self.sync()
        dircontent = os.listdir(self.folder)
        dircontent.sort()
        self.assertEquals(dircontent,
            ['.overwriteable-info', 'student1', 'student2-student3+2',
            join_dirname_id('student2-student3', assignmentgroup.id)])


class TestAssignmentDeliverySync(TestAssignmentSyncBase):
    def setUp(self):
        super(TestAssignmentDeliverySync, self).setUp()
        self.agfolder = os.path.join(self.root, 'inf1100.looong.oblig1',
                'student1')
        self.folder = os.path.join(self.agfolder, '1')
        self.infofile = os.path.join(self.folder, '.overwriteable-info')

    def test_sync(self):
        dircontent = os.listdir(self.folder)
        dircontent.sort()
        self.assertEquals(dircontent,
                ['.overwriteable-feedback.lastsave.rst', '.overwriteable-info',
                    'feedback.rst', 'files'])
        agdircontent = os.listdir(self.agfolder)
        agdircontent.sort()
        self.assertEquals(agdircontent, ['.overwriteable-info', '1'])

    def test_infofile(self):
        self.assertTrue(os.path.isfile(self.infofile))
        info = ConfigParser()
        info.read([self.infofile])
        self.assertEquals(info.get('info', 'id'), '1')
        self.assertEquals(info.get('info', 'time_of_delivery'),
                '2010-06-19 14:47:29')

    def test_add_delivery(self):
        assignmentgroup = devilry.core.models.AssignmentGroup.objects.get(id=1)
        delivery = devilry.core.models.Delivery.begin(assignmentgroup, self.student2)
        delivery.finish()
        delivery.time_of_delivery = datetime(2010, 6, 19, 14, 47, 29)
        delivery.save()
        self.sync()

        dircontent = os.listdir(self.agfolder)
        dircontent.sort()
        self.assertEquals(dircontent, ['.overwriteable-info', '1', '3']) # 2 is not successful, and ignored..

    def test_feedback(self):
        info = ConfigParser()
        info.read([self.infofile])
        self.assertRaises(NoOptionError, info.get, 'info', 'feedback_text')

        delivery = devilry.core.models.Delivery.objects.get(id=1)
        f = delivery.get_feedback()
        f.text = 'test'
        f.published = True
        f.last_modified = datetime.now()
        f.last_modified_by = self.examiner1
        f.set_grade_from_xmlrpcstring('+')
        f.save()
        self.sync()
        info = ConfigParser()
        info.read([self.infofile])
        self.assertEquals(info.get('info', 'feedback_text'), 'test')

    def test_feedback_text(self):
        delivery = devilry.core.models.Delivery.objects.get(id=1)
        f = delivery.get_feedback()
        f.text = 'test'
        f.published = True
        f.last_modified = datetime.now()
        f.last_modified_by = self.examiner1
        f.set_grade_from_xmlrpcstring('+')
        f.save()
        self.sync()
        info = ConfigParser()
        info.read([self.infofile])
        self.assertEquals(info.get('info', 'feedback_text'), 'test')


# WARNING: We are have no tests for filemeta, because all the other tests
# use the django test-client, and it does not support file-downloads using
# urllib2.


class LoginTester(cli.Login):
    def get_password(self):
        return 'test' # test-data uses this password for all users


class TestCommandBase(TestCase, XmlRpcAssertsMixin):
    """ Base class for testing subclasss of cli.Command. """
    fixtures = ['tests/xmlrpc_examiner/users',
            'tests/xmlrpc_examiner/core']

    def setUp(self):
        self.oldcwd = os.getcwd()
        self.root = mkdtemp(prefix='devilry-test')
        self.devilrydir = os.path.join(self.root, '.devilry')
        os.chdir(self.root)
        self.examiner1 = User.objects.get(username='examiner1')
        self.student2 = User.objects.get(username='student2')
        self.client = Client()
        self.init()
        self.setup_log()

    def setup_log(self):
        self.logdata = StringIO()
        self.loghandler = logging.StreamHandler(self.logdata)
        self.loghandler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s:%(message)s")
        self.loghandler.setFormatter(formatter)
        log.addHandler(self.loghandler)

    def reset_log(self):
        log.removeHandler(self.loghandler)
        self.setup_log()

    def tearDown(self):
        rmtree(self.root)
        os.chdir(self.oldcwd)
        log.removeHandler(self.loghandler)

    def create_commandcls(self, commandcls):
        server = get_serverproxy(self.client, commandcls.urlpath)
        class TestCmd(commandcls):
            def get_serverproxy(self):
                return server
            def configure_loghandlers(self, loglevel):
                pass
        return TestCmd

    def init(self):
        Init = self.create_commandcls(cli.Init)
        i = Init()
        url = 'http://localhost:8000'
        i.cli([url])
        return url

    def login(self, username):
        Login = self.create_commandcls(LoginTester)
        l = Login()
        l.cli(['-u', username])
        return l

    def read_config(self):
        c = ConfigParser()
        c.read([os.path.join(self.root, '.devilry', 'config.cfg')])
        return c


class TestInit(TestCommandBase):
    def test_init(self):
        devilrydir = os.path.join(self.root, '.devilry')
        self.assertTrue(os.path.isdir(devilrydir))
        self.assertTrue(os.path.isfile(os.path.join(devilrydir,
            'config.cfg')))
        conf = self.read_config()
        self.assertEquals(conf.get('settings', 'url'),
                'http://localhost:8000')

    def test_init_existing(self):
        self.assertRaises(SystemExit, self.init)


class TestLogin(TestCommandBase):
    def test_login_successful(self):
        Login = self.create_commandcls(LoginTester)
        l = Login()
        l.cli(['-u', 'examiner1'])
        self.assertEquals(self.logdata.getvalue().strip(),
                'INFO:Login successful')

    def test_login_invalid(self):
        Login = self.create_commandcls(LoginTester)
        l = Login()
        self.assertRaises(SystemExit, l.cli, ['-u', 'doesnotexists'])
        self.assertEquals(self.logdata.getvalue().strip(),
                'ERROR:Login failed. Reason:\nERROR:Invalid username/password.')

    def test_login_disabled(self):
        examiner1 = User.objects.get(username='examiner1')
        examiner1.is_active = False
        examiner1.save()
        Login = self.create_commandcls(LoginTester)
        l = Login()
        self.assertRaises(SystemExit, l.cli, ['-u', 'examiner1'])
        self.assertEquals(self.logdata.getvalue().strip(),
                'ERROR:Login failed. Reason:\nERROR:Your user is disabled.')


class TestListAssignments(TestCommandBase):
    def test_listassignments(self):
        self.login('examiner1')
        ListAssignments = self.create_commandcls(examinercmd.ListAssignments)
        la = ListAssignments()
        la.cli([])
        self.assertEquals(self.logdata.getvalue().strip(),
                'INFO:Login successful\n'\
                'INFO:Active assignments:\n' \
                'INFO:* inf1100.looong.oblig1')


class TestListAssignmentGroups(TestCommandBase):
    def test_listassignmentgroups(self):
        self.login('examiner1')
        ListAssignmentGroups = self.create_commandcls(examinercmd.ListAssignmentGroups)
        la = ListAssignmentGroups()
        la.cli(['inf1100.looong.oblig1'])
        self.assertEquals(self.logdata.getvalue().strip(),
            'INFO:Login successful\n' \
            'INFO:              ID  STUDENT(S)\n' \
            'INFO:              1)  student1                                      (deliveries: 2)\n' \
            'INFO:              2)  student2, student3                            (deliveries: 1)')


class TestSync(TestCommandBase):
    def test_sync(self):
        self.login('examiner1')
        Sync = self.create_commandcls(examinercmd.Sync)
        s = Sync()
        s.cli([])
        s.cli([])

        # Just a sanity test to make sure the already tested AssignmentSync
        # class is called correctly
        self.assertTrue(os.path.exists(os.path.join(self.root,
            'inf1100.looong.oblig1', 'student2-student3')))

        #print '\n'.join(["'%s\\n' \\" % x for x in self.logdata.getvalue().strip().split('\n')])
        self.assertEquals(self.logdata.getvalue().strip(),
            'INFO:Login successful\n' \
            'INFO:+ inf1100.looong.oblig1\n' \
            'INFO:+ inf1100.looong.oblig1/student1\n' \
            'DEBUG:Delivery inf1100.looong.oblig1/student1/2 was not successfully completed, and is therefore ignored.\n' \
            'INFO:+ inf1100.looong.oblig1/student1/1\n' \
            'INFO:+ inf1100.looong.oblig1/student2-student3\n' \
            'DEBUG:Delivery inf1100.looong.oblig1/student2-student3/1 was not successfully completed, and is therefore ignored.\n' \
            'DEBUG:inf1100.looong.oblig1 already exists\n' \
            'DEBUG:inf1100.looong.oblig1/student1 already exists.\n' \
            'DEBUG:Delivery inf1100.looong.oblig1/student1/2 was not successfully completed, and is therefore ignored.\n' \
            'DEBUG:inf1100.looong.oblig1/student1/1 already exists.\n' \
            'DEBUG:inf1100.looong.oblig1/student2-student3 already exists.\n' \
            'DEBUG:Delivery inf1100.looong.oblig1/student2-student3/1 was not successfully completed, and is therefore ignored.'
        )
        


class TestFeedback(TestCommandBase):

    def setUp(self):
        super(TestFeedback, self).setUp()
        self.login('examiner1')
        self.sync()
        self.reset_log()
        self.deliverypath = os.path.join(self.root, 'inf1100.looong.oblig1',
                'student1', '1')
        deliveryinfo = Info.read_open(self.deliverypath, 'Delivery')
        self.delivery = devilry.core.models.Delivery.objects.get(
                id = deliveryinfo.get_id())

    def sync(self):
        Sync = self.create_commandcls(examinercmd.Sync)
        s = Sync()
        s.cli([])

    def test_feedback_wrongcwd(self):
        Feedback = self.create_commandcls(examinercmd.Feedback)
        f = Feedback()
        self.assertRaises(SystemExit, f.cli, [])
        self.assertEquals(self.logdata.getvalue().strip(),
                'ERROR:You are not in a delivery-directory.')

    def test_feedback_wrongdirarg(self):
        Feedback = self.create_commandcls(examinercmd.Feedback)
        f = Feedback()
        self.assertRaises(SystemExit, f.cli, [''])
        self.assertEquals(self.logdata.getvalue().strip(),
                'ERROR:The given directory is not a delivery-directory.')

    def test_feedback(self):
        self.assertRaises(devilry.core.models.Feedback.DoesNotExist,
                lambda: self.delivery.feedback)
        Feedback = self.create_commandcls(examinercmd.Feedback)
        f = Feedback()
        f.cli(['-g', '+', '-t', 'ok', '-f', 'txt', self.deliverypath])
        self.assertEquals(self.logdata.getvalue().strip(),
                'DEBUG:Feedback found in commandline argument -t.\n' \
            'INFO:Feedback format: txt.\n' \
                'INFO:Feedback successfully saved.')
        self.assertEquals(self.delivery.feedback.text, 'ok')
        self.assertEquals(self.delivery.feedback.format, 'txt')
        self.assertEquals(self.delivery.feedback.get_grade_as_short_string(),
                'Approved')

    def test_feedback_from_file(self):
        self.assertRaises(devilry.core.models.Feedback.DoesNotExist,
                lambda: self.delivery.feedback)
        Feedback = self.create_commandcls(examinercmd.Feedback)
        f = Feedback()
        open(os.path.join(self.deliverypath, 'feedback.rst'), 'wb').write('ok')
        f.cli(['-g', '+', self.deliverypath])

        logvalue = self.logdata.getvalue().strip()
        self.assertEquals(logvalue,
            'DEBUG:Feedback not found in commandline argument -t. Trying file feedback.rst.\n' \
            'INFO:Found feedback in file feedback.rst.\n' \
            'INFO:Feedback format: rst.\n' \
            'INFO:Feedback successfully saved.')
        self.assertEquals(self.delivery.feedback.text, 'ok')
        self.assertEquals(self.delivery.feedback.format, 'rst')
        self.assertEquals(self.delivery.feedback.get_grade_as_short_string(),
                'Approved')
