from django.test import TransactionTestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import Period
from devilry.devilry_rest.testclient import RestClient
from devilry.devilry_qualifiesforexam.models import Status
from devilry.devilry_qualifiesforexam.pluginhelpers import create_settings_sessionkey
from devilry.devilry_qualifiesforexam.pluginhelpers import PluginResultsFailedVerification
from devilry.devilry_qualifiesforexam.registry import qualifiesforexam_plugins


def noop(*args):
    pass



class TestRestStatus(TransactionTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
            subjects=['sub'],
            periods=[
                'oldperiod:admin(periodadmin):begins(-12):ends(2)',
                'p1:admin(periodadmin):begins(-3):ends(6)',
                'p2:admin(periodadmin):begins(-1):ends(6)'])
        self.client = RestClient()
        self.url = reverse('devilry_qualifiesforexam-rest-status')
        self.testhelper.create_superuser('superuser')

        qualifiesforexam_plugins.add(
            id = 'devilry_qualifiesforexam.test.noop-plugin',
            url = '/some/noop-url',
            title = 'Noop',
            post_statussave=noop,
            description = 'noop',
            pluginsettings_summary_generator = lambda status: 'noop summary'
        )

    def tearDown(self):
        for pluginid in ('devilry_qualifiesforexam.test.plugin', 'devilry_qualifiesforexam.test.noop-plugin'):
            if pluginid in qualifiesforexam_plugins:
                del qualifiesforexam_plugins.items[pluginid]

    def _get_url(self, periodid=None):
        if periodid:
            return '{0}{1}'.format(self.url, periodid)
        else:
            return self.url

    def _create_relatedstudent(self, username, fullname=None):
        user = getattr(self.testhelper, username, None)
        if not user:
            user = self.testhelper.create_user(username, fullname=fullname)
        relstudent = self.testhelper.sub_p1.relatedstudent_set.create(user=user)
        return relstudent

    def _postas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.rest_post(self._get_url(), data)

    def _test_post_as(self, username):
        self.assertEquals(Status.objects.count(), 0)
        relatedStudent1 = self._create_relatedstudent('student1', 'Student One')
        relatedStudent2 = self._create_relatedstudent('student2', 'Student Two')
        content, response = self._postas(username, {
            'period': self.testhelper.sub_p1.id,
            'status': 'ready',
            'message': 'This is a test',
            'plugin': 'devilry_qualifiesforexam.test.noop-plugin',
            'pluginsessionid': 'tst',
            'passing_relatedstudentids': [relatedStudent1.id]
        })
        self.assertEquals(response.status_code, 201)
        self.assertEquals(Status.objects.count(), 1)
        status = Status.objects.all()[0]
        self.assertEquals(status.period, self.testhelper.sub_p1)
        self.assertEquals(status.status, 'ready')
        self.assertEquals(status.message, 'This is a test')
        self.assertEquals(status.plugin, 'devilry_qualifiesforexam.test.noop-plugin')

        self.assertEqual(status.students.count(), 2)
        qualifies1 = status.students.get(relatedstudent=relatedStudent1)
        qualifies2 = status.students.get(relatedstudent=relatedStudent2)
        self.assertTrue(qualifies1.qualifies)
        self.assertFalse(qualifies2.qualifies)

    def test_post_as_periodadmin(self):
        self._test_post_as(self.testhelper.periodadmin)

    def test_post_as_nodeadmin(self):
        self._test_post_as(self.testhelper.uniadmin)

    def test_post_as_superuser(self):
        self._test_post_as(self.testhelper.superuser)

    def test_post_as_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._postas('nobody', {
            'period': self.testhelper.sub_p1.id,
            'status': 'ready',
            'message': 'This is a test',
            'plugin': 'devilry_qualifiesforexam.test.noop-plugin',
            'pluginsessionid': 'tst',
            'passing_relatedstudentids': [10]
        })
        self.assertEqual(response.status_code, 403)

    def test_post_almostready(self):
        relatedStudent1 = self._create_relatedstudent('student1', 'Student One')
        relatedStudent2 = self._create_relatedstudent('student2', 'Student Two')
        content, response = self._postas('periodadmin', {
            'period': self.testhelper.sub_p1.id,
            'status': 'almostready',
            'message': 'This is a test',
            'plugin': 'devilry_qualifiesforexam.test.noop-plugin',
            'pluginsessionid': 'tst',
            'passing_relatedstudentids': [relatedStudent1.id],
            'notready_relatedstudentids': [relatedStudent2.id]
        })
        self.assertEquals(response.status_code, 201)
        status = Status.objects.all()[0]
        self.assertEquals(status.status, 'almostready')
        self.assertEqual(status.students.count(), 2)
        qualifies1 = status.students.get(relatedstudent=relatedStudent1)
        qualifies2 = status.students.get(relatedstudent=relatedStudent2)
        self.assertTrue(qualifies1.qualifies)
        self.assertIsNone(qualifies2.qualifies)

    def test_post_notreadystudents_with_invalidstatus(self):
        relatedStudent1 = self._create_relatedstudent('student1', 'Student One')
        content, response = self._postas('periodadmin', {
            'period': self.testhelper.sub_p1.id,
            'status': 'ready', # Could choose any status except almostready for this test to be valid
            'plugin': 'devilry_qualifiesforexam.test.noop-plugin',
            'pluginsessionid': 'tst',
            'notready_relatedstudentids': [relatedStudent1.id]
        })
        self.assertEquals(response.status_code, 400)
        self.assertEqual(content['details'],
            u'Only the ``almostready`` status allows marking students as not ready for export.')

    def test_post_notready_check_studentsignored(self):
        relatedStudent1 = self._create_relatedstudent('student1', 'Student One')
        content, response = self._postas('periodadmin', {
            'period': self.testhelper.sub_p1.id,
            'status': 'notready',
            'pluginsessionid': 'tst',
            'message': 'Test'
        })
        self.assertEquals(response.status_code, 201)
        status = Status.objects.all()[0]
        self.assertEquals(status.status, 'notready')
        self.assertEquals(status.message, 'Test')
        self.assertEqual(status.students.count(), 0)

    def test_post_notready_messagerequired(self):
        relatedStudent1 = self._create_relatedstudent('student1', 'Student One')
        content, response = self._postas('periodadmin', {
            'period': self.testhelper.sub_p1.id,
            'status': 'notready',
            'pluginsessionid': 'tst',
            'message': '  ',
            'plugin': 'devilry_qualifiesforexam.test.noop-plugin'
        })
        self.assertEquals(response.status_code, 400)
        self.assertEqual(content['errors'][0], u'Message can not be empty when status is ``notready``.')

    def test_post_invalidstatus(self):
        relatedStudent1 = self._create_relatedstudent('student1', 'Student One')
        content, response = self._postas('periodadmin', {
            'period': self.testhelper.sub_p1.id,
            'status': 'invalidstatus',
            'pluginsessionid': 'tst',
            'plugin': 'devilry_qualifiesforexam.test.noop-plugin',
            'passing_relatedstudentids': [relatedStudent1.id]
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['field_errors']['status'][0],
            u'Select a valid choice. invalidstatus is not one of the available choices.')


    def _getinstanceas(self, username, periodid):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self._get_url(periodid))

    def _test_getinstance_as(self, username):
        relatedStudent1 = self._create_relatedstudent('student1', 'Student One')
        relatedStudent2 = self._create_relatedstudent('student2', 'Student Two')
        status = Status(
            period = self.testhelper.sub_p1,
            status = 'ready',
            message = 'Test',
            user = getattr(self.testhelper, username),
            plugin = 'devilry_qualifiesforexam.test.noop-plugin'
        )
        status.save()
        status.students.create(relatedstudent=relatedStudent1, qualifies=True)
        status.students.create(relatedstudent=relatedStudent2, qualifies=False)

        content, response = self._getinstanceas(username, self.testhelper.sub_p1.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(content.keys()),
            set(['id', 'perioddata', 'statuses', u'is_active', u'short_name', u'long_name', u'subject']))
        self.assertEqual(content['id'], self.testhelper.sub_p1.id)
        statuses = content['statuses']
        self.assertEqual(len(statuses), 1)
        self.assertEqual(set(statuses[0].keys()),
            set([u'id', u'status', u'plugin', u'statustext',
                 u'period', u'passing_relatedstudentids_map',
                 u'user', u'message', u'createtime', u'pluginsettings_summary',
                 u'plugin_description', u'plugin_title']))
        self.assertEqual(statuses[0]['period'], self.testhelper.sub_p1.id)
        self.assertEqual(statuses[0]['status'], 'ready')
        self.assertEqual(statuses[0]['message'], 'Test')
        self.assertEqual(statuses[0]['plugin'], 'devilry_qualifiesforexam.test.noop-plugin')
        self.assertEqual(statuses[0]['pluginsettings_summary'], 'noop summary')
        self.assertIn(str(relatedStudent1.id), statuses[0]['passing_relatedstudentids_map'])


    def test_getinstance_as_periodadmin(self):
        self._test_getinstance_as('periodadmin')
    def test_getinstance_as_nodeadmin(self):
        self._test_getinstance_as('uniadmin')
    def test_getinstance_as_superuser(self):
        self._test_getinstance_as('superuser')

    def test_getinstanceas_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._getinstanceas('nobody', self.testhelper.sub_p1.id)
        self.assertEqual(response.status_code, 403)

    def test_getinstance_no_statuses(self):
        content, response = self._getinstanceas('periodadmin', self.testhelper.sub_p1.id)
        self.assertEqual(response.status_code, 404)
        self.assertEquals(content['detail'], u'The period has no statuses')

    def test_getinstance_invalid_period(self):
        periodid = 10000
        self.assertFalse(Period.objects.filter(id=periodid).exists()) # Just to be sure we dont get false positives
        content, response = self._getinstanceas('periodadmin', periodid)
        self.assertEqual(response.status_code, 404)
        self.assertEquals(content['detail'], u'The period with ID 10000 does not exist')



    def _getlistas(self, username, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self._get_url(), **kwargs)

    def _createlistteststatus(self, period, status='ready',
                              plugin='devilry_qualifiesforexam.test.noop-plugin'):
        status = Status(
            period = period,
            status = status,
            message = 'Test',
            user = self.testhelper.periodadmin,
            plugin = plugin
        )
        status.full_clean()
        status.save()
        return status

    def _test_getlist_as(self, username):
        self._createlistteststatus(self.testhelper.sub_oldperiod)
        self._createlistteststatus(self.testhelper.sub_p1, status='notready', plugin='')
        import time
        time.sleep(0.1) # Sleep to make sure the status below is the active status
        status = self._createlistteststatus(self.testhelper.sub_p1)

        content, response = self._getlistas(username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        p1info = content[0]
        self.assertEqual(p1info['id'], self.testhelper.sub_p1.id)
        self.assertEqual(p1info['active_status']['id'], status.id)
        p2info = content[1]
        self.assertEqual(p2info['id'], self.testhelper.sub_p2.id)
        self.assertEqual(p2info['active_status'], None)

    def test_getlist_as_periodadmin(self):
        self._test_getlist_as('periodadmin')
    def test_getlist_as_nodeadmin(self):
        self._test_getlist_as('uniadmin')
    def test_getlist_as_superuser(self):
        self._test_getlist_as('superuser')

    def test_getlist_as_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._getlistas('nobody')
        self._createlistteststatus(self.testhelper.sub_p1,
            status='notready', plugin='')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)


    def test_get_within_node(self):
        self.testhelper.add(nodes='uni.extra:admin(extraadmin)',
            subjects=['othersub'],
            periods=['p1:admin(periodadmin):begins(-3):ends(6)'])
        content, response = self._getlistas('extraadmin', node_id=self.testhelper.uni_extra.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        p1info = content[0]
        self.assertEqual(p1info['id'], self.testhelper.othersub_p1.id)

    def test_get_within_node_notactive(self):
        self.testhelper.add(nodes='uni.extra:admin(extraadmin)',
            subjects=['othersub'],
            periods=['old:admin(periodadmin):begins(-12):ends(6)'])
        content, response = self._getlistas('extraadmin', node_id=self.testhelper.uni_extra.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)

    def test_get_within_node_notadmin_on_requested(self):
        self.testhelper.add(nodes='uni.extra:admin(extraadmin)')
        content, response = self._getlistas('extraadmin', node_id=self.testhelper.uni.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)


    def test_save_settings(self):
        savedsettings = {}
        def save_settings(status, settings):
            savedsettings['status'] = status
            savedsettings['settings'] = settings

        qualifiesforexam_plugins.add(
            id = 'devilry_qualifiesforexam.test.plugin',
            url = '/some/url',
            title = 'Test',
            description = 'A test',
            uses_settings=True,
            post_statussave = save_settings
        )
        self.client.login(username='periodadmin', password='test')
        session = self.client.session
        session[create_settings_sessionkey('tst')] = {'test': 'settings'}
        session.save()
        content, response = self._postas('periodadmin', {
            'period': self.testhelper.sub_p1.id,
            'status': 'ready',
            'plugin': 'devilry_qualifiesforexam.test.plugin',
            'pluginsessionid': 'tst',
            'passing_relatedstudentids': []
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(savedsettings), 2)
        self.assertEqual(savedsettings['settings'], {'test': 'settings'})
        self.assertIsInstance(savedsettings['status'], Status)


    def test_save_settings_missing_sessiondata(self):

        def save_settings(status, settings):
            pass

        qualifiesforexam_plugins.add(
            id = 'devilry_qualifiesforexam.test.plugin',
            url = '/some/url',
            title = 'Test',
            uses_settings = True,
            description = 'A test',
            post_statussave = save_settings
        )
        self.assertEquals(Status.objects.count(), 0)
        content, response = self._postas('periodadmin', {
            'period': self.testhelper.sub_p1.id,
            'status': 'ready',
            'plugin': 'devilry_qualifiesforexam.test.plugin',
            'pluginsessionid': 'tst',
            'passing_relatedstudentids': []
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['detail'],
            u'The "devilry_qualifiesforexam.test.plugin"-plugin requires settings - no settings found in the session.')
        self.assertEquals(Status.objects.count(), 0) # The database rolled back because of the error


    def test_fail_verification(self):

        def post_statussave(status, settings):
            raise PluginResultsFailedVerification('Invalid')

        qualifiesforexam_plugins.add(
            id = 'devilry_qualifiesforexam.test.plugin',
            url = '/some/url',
            title = 'Test',
            description = 'A test',
            post_statussave = post_statussave
        )
        self.assertEquals(Status.objects.count(), 0)
        content, response = self._postas('periodadmin', {
            'period': self.testhelper.sub_p1.id,
            'status': 'ready',
            'plugin': 'devilry_qualifiesforexam.test.plugin',
            'pluginsessionid': 'tst',
            'passing_relatedstudentids': []
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['detail'], u'Invalid')
        self.assertEquals(Status.objects.count(), 0) # The database rolled back because of the error
