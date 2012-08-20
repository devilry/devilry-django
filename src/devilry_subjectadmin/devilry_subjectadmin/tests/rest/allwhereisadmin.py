from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient


class TestRestAllWhereIsAdmin(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.client = RestClient()
        self.url = '/devilry_subjectadmin/rest/allwhereisadmin/'
        self.testhelper.create_user('nobody')

    def _listas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def test_list_emptysubject(self):
        self.testhelper.add(nodes='uni',
                            subjects=['duck2000:admin(adm)'])
                            #periods=['someperiod:begins(-2):ends(6)'],
                            #assignments=['first:admin(firstadmin)',
                                         #'second:admin(secondadmin,firstadmin)',
                                         #'third'])
        content, response = self._listas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['short_name'], 'duck2000')

    def test_list_emptyperiod(self):
        self.testhelper.add(nodes='uni',
                            subjects=['duck2000:admin(adm)'],
                            periods=['p1'])
        content, response = self._listas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['short_name'], 'duck2000')
        self.assertEquals(content[0]['is_admin'], True)
        self.assertEquals(len(content[0]['periods']), 1)
        self.assertEquals(content[0]['periods'][0]['short_name'], 'p1')
        self.assertEquals(content[0]['periods'][0]['is_admin'], False)

        self.testhelper.add(nodes='uni',
                            subjects=['duck3000'],
                            periods=['p1:admin(adm)'])
        content, response = self._listas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 2)
