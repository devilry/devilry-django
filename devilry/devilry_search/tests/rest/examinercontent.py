from datetime import datetime, timedelta
import unittest
from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_rest.testclient import RestClient
from .base import HaystackTestSettings
from .base import AssertSearchResultMixin


@unittest.skip
class TestRestSearchExaminerContent(TestCase, AssertSearchResultMixin):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni:ln(Test Uni)',
            subjects=['sub:ln(Test Sub)'],
            periods=['p1:begins(-2):ln(Test P1)'],
            assignments=['a1:ln(Test A1)'],
            assignmentgroups=[
                'TestGroup1:candidate(student1):examiner(examiner1)',
                'TestGroup2:candidate(student2):examiner(examiner2,examiner1)',
                'TestGroup3:candidate(examiner1)',
                'TestGroup4:candidate(student4):examiner(examiner2)'
            ]
        )

        self.client = RestClient()
        self.url = reverse('devilry_search_examinercontent')

    def _getas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def test_perms_examiner(self):
        with HaystackTestSettings():
            content, response = self._getas('examiner1', search='Test')
            matches = content['matches']
            self.assertEqual(len(matches), 3)
            self.assert_has_search_result(matches, type='core_assignmentgroup',
                title='Test A1', name='TestGroup1', students=['student1'])
            self.assert_has_search_result(matches, type='core_assignmentgroup',
                title='Test A1', name='TestGroup2', students=['student2'])
            self.assert_has_search_result(matches, type='core_assignment', title='Test A1')


    def test_perms_examiner_not_published(self):
        self.testhelper.sub_p1_a1.publishing_time = datetime.now() + timedelta(days=1)
        self.testhelper.sub_p1_a1.save()
        with HaystackTestSettings():
            content, response = self._getas('examiner1', search='Test')
            matches = content['matches']
            self.assertEqual(len(matches), 0)


    def test_anonymous(self):
        self.testhelper.sub_p1_a1.anonymous = True
        self.testhelper.sub_p1_a1.save()
        student2candidate = self.testhelper.sub_p1_a1_TestGroup2.candidates.all()[0]
        student2candidate.candidate_id = 'secret'
        student2candidate.save()
        with HaystackTestSettings():
            content, response = self._getas('examiner1', search='Test')
            matches = content['matches']
            self.assertEqual(len(matches), 3)
            self.assert_has_search_result(matches, type='core_assignmentgroup',
                title='Test A1', name='TestGroup1', students=[None])
            self.assert_has_search_result(matches, type='core_assignmentgroup',
                title='Test A1', name='TestGroup2', students=['secret'])
            self.assert_has_search_result(matches, type='core_assignment', title='Test A1')

    def test_can_search_for_students(self):
        with HaystackTestSettings():
            content, response = self._getas('examiner1', search='student1')
            matches = content['matches']
            self.assertEqual(len(matches), 1)
            self.assert_has_search_result(matches, type='core_assignmentgroup',
                title='Test A1', name='TestGroup1')

    def test_anonymous_no_search_bleeding(self):
        self.testhelper.sub_p1_a1.anonymous = True
        self.testhelper.sub_p1_a1.save()
        with HaystackTestSettings():
            content, response = self._getas('examiner1', search='student1')
            matches = content['matches']
            self.assertEqual(len(matches), 0)
