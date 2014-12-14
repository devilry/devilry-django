from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient



class TestRestExaminerStats(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
            subjects=['sub'],
            periods=['p1:begins(-3):ends(6)'],
            assignments=['a1:admin(assignmentadmin)']
        )
        self.client = RestClient()
        self.testhelper.create_superuser('superuser')

    def _get_url(self, assignmentid):
        return reverse('devilry-subjectadmin-rest-examinerstats', kwargs={'id': assignmentid})

    def _getas(self, username, periodid):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self._get_url(periodid))

    def _test_get_as(self, username):
        content, response = self._getas(username, self.testhelper.sub_p1_a1.id)
        self.assertEqual(response.status_code, 200)

    def test_perms_as_assignmentadmin(self):
        self._test_get_as('assignmentadmin')
    def test_perms_as_nodeadmin(self):
        self._test_get_as('uniadmin')
    def test_perms_as_superuser(self):
        self._test_get_as('superuser')

    def test_perms_as_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._getas('nobody', self.testhelper.sub_p1_a1.id)
        self.assertEqual(response.status_code, 403)

    def test_perms_invalid_id(self):
        content, response = self._getas('assignmentadmin', 10000)
        self.assertEqual(response.status_code, 403)
