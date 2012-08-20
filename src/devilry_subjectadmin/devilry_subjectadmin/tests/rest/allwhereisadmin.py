from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient


class TestRestAllWhereIsAdmin(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.client = RestClient()
        self.url = '/devilry_subjectadmin/rest/allwhereisadmin/'

    def _listas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def test_list_emptysubject(self):
        self.testhelper.add(nodes='uni',
                            subjects=['duck2000:admin(adm)'])
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

    def test_list_nobody(self):
        self.testhelper.create_user('nobody')
        self.testhelper.add(nodes='uni',
                            subjects=['duck2000'])
        content, response = self._listas('nobody')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 0)

    def test_list(self):
        self.testhelper.add(nodes='uni',
                            subjects=['duck2000:admin(adm)', 'duck3000', 'duck4000'])
        self.testhelper.add_to_path('uni;duck2000.p1')
        self.testhelper.add_to_path('uni;duck3000.p1:admin(adm)')
        self.testhelper.add_to_path('uni;duck4000.p1.a1:admin(adm)')
        content, response = self._listas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 3)

        self.assertEquals(content[0]['short_name'], 'duck2000')
        self.assertEquals(content[0]['is_admin'], True)
        self.assertEquals(content[0]['can_administer'], True)
        self.assertEquals(len(content[0]['periods']), 1)
        self.assertEquals(content[0]['periods'][0]['can_administer'], True)
        self.assertEquals(content[0]['periods'][0]['is_admin'], False)

        self.assertEquals(content[1]['short_name'], 'duck3000')
        self.assertEquals(content[1]['is_admin'], False)
        self.assertEquals(content[1]['can_administer'], False)
        self.assertEquals(len(content[1]['periods']), 1)
        self.assertEquals(content[1]['periods'][0]['can_administer'], True)
        self.assertEquals(content[1]['periods'][0]['is_admin'], True)

        self.assertEquals(content[2]['short_name'], 'duck4000')
        self.assertEquals(content[2]['is_admin'], False)
        self.assertEquals(content[2]['can_administer'], False)
        self.assertEquals(len(content[2]['periods']), 1)
        self.assertEquals(content[2]['periods'][0]['can_administer'], False)
        self.assertEquals(content[2]['periods'][0]['is_admin'], False)
        self.assertEquals(len(content[2]['periods'][0]['assignments']), 1)
        self.assertEquals(content[2]['periods'][0]['assignments'][0]['can_administer'], True)
        self.assertEquals(content[2]['periods'][0]['assignments'][0]['is_admin'], True)
