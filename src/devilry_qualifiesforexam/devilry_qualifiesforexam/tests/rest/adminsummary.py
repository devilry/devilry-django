from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient
from devilry_qualifiesforexam.models import Status


class TestAdminSummaryResource(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.client = RestClient()
        self.testhelper.create_superuser('superuser')

    def _get_url(self, **kwargs):
        return reverse('devilry_qualifiesforexam-adminsummary', kwargs=kwargs)

    def _getas(self, username, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self._get_url(**kwargs))

    def _test_getall_as(self, username):
        self.testhelper.add(nodes='uni:admin(uniadmin).ifi',
            subjects=['duck101', 'duck202', 'duck303'],
            periods=['p1:begins(-3):ends(6)'])
        for period in (self.testhelper.duck101_p1, self.testhelper.duck202_p1):
            Status.objects.create(period=period, status=Status.READY,
                    user=self.testhelper.superuser)

        content, response = self._getas(username)
        self.assertEqual(response.status_code, 200)
        from pprint import pprint
        pprint(content)

    def test_get_as_uniadmin(self):
        self._test_getall_as('uniadmin')
    def test_get_as_superuser(self):
        self._test_getall_as('superuser')

    #def test_getas_nobody(self):
        #self.testhelper.create_user('nobody')
        #content, response = self._getas('nobody', self.testhelper.sub_p1.id,
            #PreviewData(passing_relatedstudentids=[]))
        #self.assertEqual(response.status_code, 403)

    #def test_get_invalid_period(self):
        #periodid = 10000
        #self.assertFalse(Period.objects.filter(id=periodid).exists()) # Just to be sure we dont get false positives
        #content, response = self._getas('periodadmin', periodid, PreviewData(passing_relatedstudentids=[]))
        #self.assertEqual(response.status_code, 403)
