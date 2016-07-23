# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django import test
from django.conf import settings
from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.devilry_api.assignment.views import assignment_student
from devilry.devilry_api.tests.mixins import test_auth_student, api_test_helper


class TestAssignmentListView(test_auth_student.TestAuthAPIKeyStudentMixin,
                             api_test_helper.TestCaseMixin,
                             APITestCase):
    viewclass = assignment_student.AssignmentListView
    route = '/assignment/student/list/'

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_sanity(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        response = self.mock_get_request(requestuser=candidate.relatedstudent.user)
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.parentnode.short_name, response.data[0]['subject'])
        self.assertEqual(str(assignment.long_name), response.data[0]['long_name'])
        self.assertEqual(assignment.short_name, response.data[0]['short_name'])
        self.assertEqual(assignment.parentnode.short_name, response.data[0]['semester'])
        self.assertEqual(assignment.publishing_time.isoformat(), response.data[0]['publishing_time'])
        self.assertEqual(assignment.first_deadline.isoformat(), response.data[0]['first_deadline'])
        self.assertEqual(assignment.anonymizationmode, response.data[0]['anonymizationmode'])
        self.assertEqual(assignment.max_points, response.data[0]['max_points'])
        self.assertEqual(assignment.passing_grade_min_points, response.data[0]['passing_grade_min_points'])
        self.assertEqual(assignment.deadline_handling, response.data[0]['deadline_handling'])
        self.assertEqual(assignment.delivery_types, response.data[0]['delivery_types'])

    def test_filter_search_subject_not_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__parentnode__short_name='duckduck1010')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        response = self.mock_get_request(requestuser=candidate.relatedstudent.user,
                                         queryparams='?search=123')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_search_subject_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__parentnode__short_name='duckduck1010')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        response = self.mock_get_request(requestuser=candidate.relatedstudent.user,
                                         queryparams='?search=duckduck1010')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.parentnode.short_name, response.data[0]['subject'])

    def test_filter_search_semester_not_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__short_name='asd')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        response = self.mock_get_request(requestuser=candidate.relatedstudent.user,
                                         queryparams='?search=S16')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_search_semester_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__short_name='S15')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        response = self.mock_get_request(requestuser=candidate.relatedstudent.user,
                                         queryparams='?search=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.short_name, response.data[0]['semester'])

    def test_filter_semester_not_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__short_name='S07')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        response = self.mock_get_request(requestuser=candidate.relatedstudent.user,
                                         queryparams='?semester=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_semester_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__short_name='S15')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        response = self.mock_get_request(requestuser=candidate.relatedstudent.user,
                                         queryparams='?semester=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.short_name, response.data[0]['semester'])

    def test_filter_subject_not_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__parentnode__short_name='duck1010')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        response = self.mock_get_request(requestuser=candidate.relatedstudent.user,
                                         queryparams='?subject=duck1000')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_subject_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__parentnode__short_name='duck1010')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        response = self.mock_get_request(requestuser=candidate.relatedstudent.user,
                                         queryparams='?subject=duck1010')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.parentnode.short_name, response.data[0]['subject'])

    def test_ordering_deadline_asc(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment1 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        assignment2 = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_start')
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=assignment1)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=assignment2)
        response = self.mock_get_request(requestuser=testuser,
                                         queryparams='?ordering=first_deadline')
        self.assertEqual(200, response.status_code)
        assignment_names = [assignment['first_deadline'] for assignment in response.data]
        self.assertListEqual([assignment2.first_deadline.isoformat(), assignment1.first_deadline.isoformat()],
                             assignment_names)

    def test_ordering_deadline_desc(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment1 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        assignment2 = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_start')
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=assignment1)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=assignment2)
        response = self.mock_get_request(requestuser=testuser,
                                         queryparams='?ordering=-first_deadline')
        self.assertEqual(200, response.status_code)
        assignment_names = [assignment['first_deadline'] for assignment in response.data]
        self.assertListEqual([assignment1.first_deadline.isoformat(), assignment2.first_deadline.isoformat()],
                             assignment_names)
