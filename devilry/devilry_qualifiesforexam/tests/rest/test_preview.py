from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import Period
from devilry.devilry_rest.testclient import RestClient
from devilry.devilry_qualifiesforexam.pluginhelpers import PreviewData


class TestRestPreview(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin)',
            subjects=['sub'],
            periods=['p1:admin(periodadmin):begins(-3):ends(6)'])
        self.client = RestClient()
        self.testhelper.create_superuser('superuser')

    def _get_url(self, periodid):
        return reverse('devilry_qualifiesforexam-rest-preview', kwargs={'id': periodid})

    def _getas(self, username, periodid, previewdata, pluginsessionid='tst'):
        self.client.login(username=username, password='test')
        session = self.client.session
        session['qualifiesforexam-{0}'.format(pluginsessionid)] = previewdata.serialize()
        session.save()
        return self.client.rest_get(self._get_url(periodid),
            pluginsessionid=pluginsessionid)

    def _test_getas(self, username):
        content, response = self._getas(username, self.testhelper.sub_p1.id,
            PreviewData(passing_relatedstudentids=[1, 2, 4]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(content.keys()), set(['pluginoutput', 'perioddata']))
        self.assertEqual(content['pluginoutput'],
            {u'passing_relatedstudentids': [1, 2, 4]})

    def test_get_as_periodadmin(self):
        self._test_getas('periodadmin')
    def test_get_as_nodeadmin(self):
        self._test_getas('uniadmin')
    def test_get_as_superuser(self):
        self._test_getas('superuser')

    def test_getas_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._getas('nobody', self.testhelper.sub_p1.id,
            PreviewData(passing_relatedstudentids=[]))
        self.assertEqual(response.status_code, 403)

    def test_get_invalid_period(self):
        periodid = 10000
        self.assertFalse(Period.objects.filter(id=periodid).exists()) # Just to be sure we dont get false positives
        content, response = self._getas('periodadmin', periodid, PreviewData(passing_relatedstudentids=[]))
        self.assertEqual(response.status_code, 403)
