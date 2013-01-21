from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient
from .base import HaystackTestSettings
from .base import AssertSearchResultMixin



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

    def test_perms_uniadmin(self):
        with HaystackTestSettings():
            content, response = self._getas('uniadmin', search='Test')
            self.assertEqual(len(content), 5)
            self.assert_has_search_result(content, modeltype='core_node', title='Test Uni')
            self.assert_has_search_result(content, modeltype='core_subject', title='Test Sub')
            self.assert_has_search_result(content, modeltype='core_period', title='Test P1')
            self.assert_has_search_result(content, modeltype='core_assignment', title='Test A1')
            self.assert_has_search_result(content, modeltype='core_assignmentgroup',
                title='Test A1', meta='student1')

    def test_perms_subjectadmin(self):
        with HaystackTestSettings():
            content, response = self._getas('subadmin', search='Test')
            self.assertEqual(len(content), 4)
            self.assert_has_search_result(content, modeltype='core_subject', title='Test Sub')
            self.assert_has_search_result(content, modeltype='core_period', title='Test P1')
            self.assert_has_search_result(content, modeltype='core_assignment', title='Test A1')
            self.assert_has_search_result(content, modeltype='core_assignmentgroup',
                title='Test A1', meta='student1')

    def test_perms_periodadmin(self):
        with HaystackTestSettings():
            content, response = self._getas('p1admin', search='Test')
            self.assertEqual(len(content), 3)
            self.assert_has_search_result(content, modeltype='core_period', title='Test P1')
            self.assert_has_search_result(content, modeltype='core_assignment', title='Test A1')
            self.assert_has_search_result(content, modeltype='core_assignmentgroup',
                title='Test A1', meta='student1')

    def test_perms_assignmentadmin(self):
        with HaystackTestSettings():
            content, response = self._getas('a1admin', search='Test')
            self.assertEqual(len(content), 2)
            self.assert_has_search_result(content, modeltype='core_assignment', title='Test A1')
            self.assert_has_search_result(content, modeltype='core_assignmentgroup',
                title='Test A1', meta='student1')

