from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.rest_testclient import RestClient
from .base import HaystackTestSettings
from .base import AssertSearchResultMixin



class TestRestSearchStudentContent(TestCase, AssertSearchResultMixin):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:ln(Test Uni)',
            subjects=['sub:ln(Test Sub)'],
            periods=['p1:begins(-2):ln(Test P1)'],
            assignments=['a1:ln(Test A1)'],
            assignmentgroups=[
                'TestGroup1:candidate(student1)',
                'TestGroup2:candidate(student2,student1)'
            ]
        )

        self.client = RestClient()
        self.url = reverse('devilry_search_studentcontent')

    def _getas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def test_perms_student(self):
        with HaystackTestSettings():
            content, response = self._getas('student1', search='Test')
            from pprint import pprint
            pprint(content)
            self.assertEqual(len(content), 2)
            self.assert_has_search_result(content, modeltype='core_assignmentgroup',
                title='Test A1', meta='student1')
            self.assert_has_search_result(content, modeltype='core_assignmentgroup',
                title='Test A1', meta='student2, student1')