import unittest
from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient
from .base import HaystackTestSettings
from .base import AssertSearchResultMixin


@unittest.skip
class TestRestSearchAdminContent(TestCase, AssertSearchResultMixin):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:admin(uniadmin):ln(Test Uni)',
            subjects=['sub:admin(subadmin):ln(Test Sub)'],
            periods=['p1:begins(-2):admin(p1admin):ln(Test P1)'],
            assignments=['a1:admin(a1admin):ln(Test A1)'],
            assignmentgroups=['TestGroup1:candidate(student1)']
        )

        self.client = RestClient()
        self.url = reverse('devilry_search_admincontent')

    def _getas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def _test_perms_topnodeorsuper(self, username):
        with HaystackTestSettings():
            content, response = self._getas(username, search='Test')
            matches = content['matches']
            self.assertEqual(len(matches), 5)
            self.assert_has_search_result(matches, type='core_node', title='Test Uni')
            self.assert_has_search_result(matches, type='core_subject', title='Test Sub')
            self.assert_has_search_result(matches, type='core_period', title='Test P1')
            self.assert_has_search_result(matches, type='core_assignment', title='Test A1')
            self.assert_has_search_result(matches, type='core_assignmentgroup',
                title='Test A1', students=['student1'])

    def test_perms_uniadmin(self):
        self._test_perms_topnodeorsuper('uniadmin')

    def test_perms_superuser(self):
        self.testhelper.create_superuser('superuser')
        self._test_perms_topnodeorsuper('superuser')

    def test_perms_subjectadmin(self):
        with HaystackTestSettings():
            content, response = self._getas('subadmin', search='Test')
            matches = content['matches']
            self.assertEqual(len(matches), 4)
            self.assert_has_search_result(matches, type='core_subject', title='Test Sub')
            self.assert_has_search_result(matches, type='core_period', title='Test P1')
            self.assert_has_search_result(matches, type='core_assignment', title='Test A1')
            self.assert_has_search_result(matches, type='core_assignmentgroup',
                title='Test A1', students=['student1'])

    def test_perms_periodadmin(self):
        with HaystackTestSettings():
            content, response = self._getas('p1admin', search='Test')
            matches = content['matches']
            self.assertEqual(len(matches), 3)
            self.assert_has_search_result(matches, type='core_period', title='Test P1')
            self.assert_has_search_result(matches, type='core_assignment', title='Test A1')
            self.assert_has_search_result(matches, type='core_assignmentgroup',
                title='Test A1', students=['student1'])

    def test_perms_assignmentadmin(self):
        with HaystackTestSettings():
            content, response = self._getas('a1admin', search='Test')
            matches = content['matches']
            self.assertEqual(len(matches), 2)
            self.assert_has_search_result(matches, type='core_assignment', title='Test A1')
            self.assert_has_search_result(matches, type='core_assignmentgroup',
                title='Test A1', students=['student1'])

