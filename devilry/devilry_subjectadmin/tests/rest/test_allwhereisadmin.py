from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient


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
        self.testhelper.add_to_path('uni;duck2000.p2000')
        self.testhelper.add_to_path('uni;duck3000.p3000:admin(adm)')
        self.testhelper.add_to_path('uni;duck4000.p4000.a1:admin(adm)')
        content, response = self._listas('adm')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 3)

        self.assertEquals(content[0]['short_name'], 'duck2000')
        self.assertEquals(content[0]['is_admin'], True)
        self.assertEquals(content[0]['can_administer'], True)
        self.assertEquals(len(content[0]['periods']), 1)
        self.assertEquals(content[0]['periods'][0]['short_name'], 'p2000')
        self.assertEquals(content[0]['periods'][0]['can_administer'], True)
        self.assertEquals(content[0]['periods'][0]['is_admin'], False)

        self.assertEquals(content[1]['short_name'], 'duck3000')
        self.assertEquals(content[1]['is_admin'], False)
        self.assertEquals(content[1]['can_administer'], False)
        self.assertEquals(len(content[1]['periods']), 1)
        self.assertEquals(content[1]['periods'][0]['short_name'], 'p3000')
        self.assertEquals(content[1]['periods'][0]['can_administer'], True)
        self.assertEquals(content[1]['periods'][0]['is_admin'], True)

        self.assertEquals(content[2]['short_name'], 'duck4000')
        self.assertEquals(content[2]['is_admin'], False)
        self.assertEquals(content[2]['can_administer'], False)
        self.assertEquals(len(content[2]['periods']), 1)
        self.assertEquals(content[2]['periods'][0]['can_administer'], False)
        self.assertEquals(content[2]['periods'][0]['is_admin'], False)
        self.assertEquals(len(content[2]['periods'][0]['assignments']), 1)
        self.assertEquals(content[2]['periods'][0]['short_name'], 'p4000')
        self.assertEquals(content[2]['periods'][0]['assignments'][0]['can_administer'], True)
        self.assertEquals(content[2]['periods'][0]['assignments'][0]['is_admin'], True)


    def test_list_active_noassignments(self):
        self.testhelper.add(nodes='uni',
                            subjects=['duck2000:admin(adm)'],
                            periods=['p1:begins(-20)', 'p2:begins(-1)', 'p3:begins(20)'])
        content, response = self._listas('adm', only_active='yes')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['short_name'], 'duck2000')
        self.assertEquals(len(content[0]['periods']), 1)
        self.assertEquals(content[0]['periods'][0]['short_name'], 'p2')

    def test_list_active(self):
        self.testhelper.add(nodes='uni',
                            subjects=['duck2000:admin(adm)'],
                            periods=['p1:begins(-20)', 'p2:begins(-1)', 'p3:begins(20)'],
                            assignments=['a1'])
        content, response = self._listas('adm', only_active='yes')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['short_name'], 'duck2000')
        self.assertEquals(len(content[0]['periods']), 1)
        self.assertEquals(content[0]['periods'][0]['short_name'], 'p2')
        self.assertEquals(len(content[0]['periods'][0]['assignments']), 1)

    def test_list_multi_active_assignments(self):
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-2):ends(6)',
                                     'p2:begins(-1):ends(6)'],
                            assignments=['a1:admin(a1admin)'])
        content, response = self._listas('a1admin', only_active='yes')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        periods = content[0]['periods']
        self.assertEquals(len(periods), 2)
        self.assertEquals(periods[0]['short_name'], 'p2')
        self.assertEquals(periods[1]['short_name'], 'p1')
        self.assertEquals(periods[0]['assignments'][0]['short_name'], 'a1')
        self.assertEquals(periods[1]['assignments'][0]['short_name'], 'a1')
