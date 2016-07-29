# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf import settings
from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.devilry_api import devilry_api_mommy_factories
from devilry.devilry_api.assignment.views import assignment_student
from devilry.devilry_api.tests.mixins import test_student_mixins, api_test_helper, test_common_mixins


class TestAssignmentListView(test_common_mixins.TestReadOnlyPermissionMixin,
                             test_student_mixins.TestAuthAPIKeyStudentMixin,
                             api_test_helper.TestCaseMixin,
                             APITestCase):
    viewclass = assignment_student.AssignmentListView

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_sanity(self):
        assignment = mommy.make('core.Assignment')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)

    def test_id(self):
        assignment = mommy.make('core.Assignment', id=10)
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(10, response.data[0]['id'])

    def test_long_name(self):
        assignment = mommy.make('core.Assignment', long_name='Assignment 1')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual('Assignment 1', response.data[0]['long_name'])

    def test_short_name(self):
        assignment = mommy.make('core.Assignment', short_name='assignment1')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual('assignment1', response.data[0]['short_name'])

    def test_period_short_name(self):
        assignment = mommy.make('core.Assignment', parentnode__short_name='V15')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual('V15', response.data[0]['period_short_name'])

    def test_subject_short_name(self):
        assignment = mommy.make('core.Assignment', parentnode__parentnode__short_name='Duck1010')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual('Duck1010', response.data[0]['subject_short_name'])

    def test_publishing_time(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.publishing_time.isoformat(), response.data[0]['publishing_time'])

    def test_anonymizationmode(self):
        assignment = mommy.make('core.Assignment')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.anonymizationmode, response.data[0]['anonymizationmode'])

    def test_num_queries(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        for x in range(10):
            assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
            mommy.make('core.Candidate',
                       relatedstudent__user=testuser,
                       assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=testuser)
        with self.assertNumQueries(2):
            self.mock_get_request(apikey=apikey.key)


class TestAssignmentListViewFilters(api_test_helper.TestCaseMixin, APITestCase):
    viewclass = assignment_student.AssignmentListView

    def test_filter_search_subject_short_name_not_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__parentnode__short_name='duckduck1010')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=123')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_search_subject_short_name_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__parentnode__short_name='duckduck1010')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=duckduck1010')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.parentnode.short_name, response.data[0]['subject_short_name'])

    def test_filter_search_period_short_name_not_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__short_name='asd')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=S16')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_search_period_short_name_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__short_name='S15')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.short_name, response.data[0]['period_short_name'])

    def test_filter_search_short_name_not_found(self):
        assignment = mommy.make('core.Assignment', short_name='assignment1')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=assignment0')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_search_short_name_found(self):
        assignment = mommy.make('core.Assignment', short_name='assignment1')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=assignment1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.short_name, response.data[0]['short_name'])

    def test_filter_subject_short_name_not_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__parentnode__short_name='duck1010')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?subject_short_name=duck1000')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_subject_short_name_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__parentnode__short_name='duck1010')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?subject_short_name=duck1010')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.parentnode.short_name, response.data[0]['subject_short_name'])

    def test_filter_period_short_name_not_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__short_name='S07')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?period_short_name=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_period_short_name_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__short_name='S15')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?period_short_name=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.short_name, response.data[0]['period_short_name'])

    def test_filter_short_name_not_found(self):
        assignment = mommy.make('core.Assignment', short_name='assignment1')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?short_name=assignment0')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_short_name_found(self):
        assignment = mommy.make('core.Assignment', short_name='assignment1')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?short_name=assignment1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.short_name, response.data[0]['short_name'])

    def test_ordering_publishing_time_asc(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment1 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        assignment2 = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_start')
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=assignment1)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=assignment2)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=testuser)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?ordering=publishing_time')
        self.assertEqual(200, response.status_code)
        assignment_publishing_time = [assignment['publishing_time'] for assignment in response.data]
        self.assertListEqual([assignment2.publishing_time.isoformat(),
                              assignment1.publishing_time.isoformat()], assignment_publishing_time)

    def test_ordering_publishing_time_desc(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment1 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        assignment2 = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_start')
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=assignment1)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=assignment2)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=testuser)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?ordering=-publishing_time')
        self.assertEqual(200, response.status_code)
        assignment_publishing_time = [assignment['publishing_time'] for assignment in response.data]
        self.assertListEqual([assignment1.publishing_time.isoformat(), assignment2.publishing_time.isoformat()],
                             assignment_publishing_time)
