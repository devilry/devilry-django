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
            periods=['p1:admin(p1admin)'])
        self.client = RestClient()
        self.url = '/devilry_qualifiesforexam/rest/status'

    def _create_relatedstudent(self, username, fullname=None):
        user = getattr(self.testhelper, username, None)
        if not user:
            user = self.testhelper.create_user(username, fullname=fullname)
        relstudent = self.testhelper.sub_p1.relatedstudent_set.create(user=user)
        return relstudent

    def _postas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.rest_post(self.url, data)

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
        self.testhelper.create_superuser('superuser')
        self._test_post_as(self.testhelper.superuser)