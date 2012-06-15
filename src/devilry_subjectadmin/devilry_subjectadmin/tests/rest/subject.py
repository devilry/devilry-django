from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient


class TestRestListSubjectRest(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['duck2000:admin(adminone,admintwo):ln(Something fancy)',
                                      'duck3000',
                                      'duck1000:admin(adminone)',
                                      'duck4000:admin(adminone,admintwo,singleadmin)'])
        self.client = RestClient()
        self.url = '/devilry_subjectadmin/rest/subject/'

    def _listas(self, username):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url)

    def test_list(self):
        content, response = self._listas('adminone')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 3)
        self.assertEquals(content[0]['short_name'], 'duck1000')
        self.assertEquals(content[1]['short_name'], 'duck2000')
        self.assertEquals(content[1]['long_name'], 'Something fancy')
        self.assertEquals(content[2]['short_name'], 'duck4000')
        self.assertEquals(set(content[0].keys()),
                          set(['parentnode_id', 'etag', 'short_name', 'long_name']))

    def test_singleadmin(self):
        content, response = self._listas('singleadmin')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['short_name'], 'duck4000')

    def test_nonadmin(self):
        self.testhelper.create_user('otheruser')
        content, response = self._listas('otheruser')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 0)
