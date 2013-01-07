from django.test import TestCase
from django.contrib.auth.models import User

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient
from devilry_qualifiesforexam.models import Status



class TestRestStatus(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
            subjects=['sub'],
            periods=[
                'oldperiod:admin(p1admin):begins(-12):ends(2)',
                'p1:admin(p1admin):begins(-2):ends(6)'])
        self.client = RestClient()
        self.url = '/devilry_qualifiesforexam/rest/status/'
        self.testhelper.create_superuser('superuser')

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
            'plugin': 'devilry_qualifiesforexam_approved.all',
            'pluginsettings': 'test',
            'passing_relatedstudentids': [relatedStudent1.id]
        })
        self.assertEquals(response.status_code, 201)
        self.assertEquals(Status.objects.count(), 1)
        status = Status.objects.all()[0]
        self.assertEquals(status.period, self.testhelper.sub_p1)
        self.assertEquals(status.status, 'ready')
        self.assertEquals(status.message, 'This is a test')
        self.assertEquals(status.plugin, 'devilry_qualifiesforexam_approved.all')
        self.assertEquals(status.pluginsettings, 'test')

        self.assertEqual(status.students.count(), 2)
        qualifies1 = status.students.get(relatedstudent=relatedStudent1)
        qualifies2 = status.students.get(relatedstudent=relatedStudent2)
        self.assertTrue(qualifies1.qualifies)
        self.assertFalse(qualifies2.qualifies)

    def test_post_as_periodadmin(self):
        self._test_post_as(self.testhelper.p1admin)

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
            'plugin': 'devilry_qualifiesforexam_approved.all',
            'pluginsettings': 'test',
            'passing_relatedstudentids': [10]
        })
        self.assertEqual(response.status_code, 403)


    def _getinstanceas(self, username):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self._get_url(self.testhelper.sub_p1.id))

    def _test_getinstance_as(self, username):
        relatedStudent1 = self._create_relatedstudent('student1', 'Student One')
        relatedStudent2 = self._create_relatedstudent('student2', 'Student Two')
        status = Status(
            period = self.testhelper.sub_p1,
            status = 'ready',
            message = 'Test',
            user = getattr(self.testhelper, username),
            plugin = 'devilry_qualifiesforexam_approved.all',
            pluginsettings = 'tst'
        )
        status.save()
        status.students.create(relatedstudent=relatedStudent1, qualifies=True)
        status.students.create(relatedstudent=relatedStudent2, qualifies=False)

        content, response = self._getinstanceas(username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(content.keys()),
            set(['id', 'perioddata', 'statuses', u'short_name', u'long_name', u'subject']))
        self.assertEqual(content['id'], self.testhelper.sub_p1.id)
        statuses = content['statuses']
        self.assertEqual(len(statuses), 1)
        self.assertEqual(set(statuses[0].keys()),
            set([u'id', u'status', u'plugin',
                 u'period', u'passing_relatedstudentids_map',
                 u'pluginsettings', u'user', u'message', u'createtime']))
        self.assertEqual(statuses[0]['period'], self.testhelper.sub_p1.id)
        self.assertEqual(statuses[0]['status'], 'ready')
        self.assertEqual(statuses[0]['message'], 'Test')
        self.assertEqual(statuses[0]['plugin'], 'devilry_qualifiesforexam_approved.all')
        self.assertEqual(statuses[0]['pluginsettings'], 'tst')
        self.assertIn(str(relatedStudent1.id), statuses[0]['passing_relatedstudentids_map'])


    def test_getinstance_as_periodadmin(self):
        self._test_getinstance_as('p1admin')
    def test_getinstance_as_nodeadmin(self):
        self._test_getinstance_as('uniadmin')
    def test_getinstance_as_superuser(self):
        self._test_getinstance_as('superuser')

    def test_getinstanceas_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._getinstanceas('nobody')
        self.assertEqual(response.status_code, 403)


    def _getlistas(self, username):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self._get_url())

    def _createlistteststatus(self, period, status='ready'):
        status = Status(
            period = period,
            status = status,
            message = 'Test',
            user = self.testhelper.p1admin,
            plugin = 'devilry_qualifiesforexam_approved.all',
            pluginsettings = 'tst'
        )
        status.full_clean()
        status.save()
        return status

    def _test_getlist_as(self, username):
        relatedStudent1 = self._create_relatedstudent('student1', 'Student One')
        relatedStudent2 = self._create_relatedstudent('student2', 'Student Two')

        self._createlistteststatus(self.testhelper.sub_oldperiod)
        self._createlistteststatus(self.testhelper.sub_p1, status='notready')
        import time
        time.sleep(0.1)
        status = self._createlistteststatus(self.testhelper.sub_p1)
        status.students.create(relatedstudent=relatedStudent1, qualifies=True)
        status.students.create(relatedstudent=relatedStudent2, qualifies=False)

        content, response = self._getlistas(username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        periodinfo = content[0]
        self.assertEqual(periodinfo['id'], self.testhelper.sub_p1.id)
        self.assertEqual(periodinfo['active_status']['id'], status.id)

    def test_getlist_as_periodadmin(self):
        self._test_getlist_as('p1admin')
    def test_getlist_as_nodeadmin(self):
        self._test_getlist_as('uniadmin')
    def test_getlist_as_superuser(self):
        self._test_getlist_as('superuser')

    def test_getlist_as_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._getlistas('nobody')
        self._createlistteststatus(self.testhelper.sub_p1, status='notready')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)