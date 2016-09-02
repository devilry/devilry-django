# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.apps.core import devilry_core_mommy_factories
from devilry.apps.core.models import Assignment
from devilry.devilry_api import devilry_api_mommy_factories
from devilry.devilry_api.feedbackset.views import feedbackset_student
from devilry.devilry_api.tests.mixins import test_student_mixins, api_test_helper, test_common_mixins
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group.models import FeedbackSet


class TestFeedbacksetSanity(test_common_mixins.TestReadOnlyPermissionMixin,
                            test_student_mixins.TestAuthAPIKeyStudentMixin,
                            api_test_helper.TestCaseMixin,
                            APITestCase):
    viewclass = feedbackset_student.FeedbacksetViewStudent

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_sanity(self):
        feedbackset = mommy.make('devilry_group.Feedbackset')
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)

    def test_id(self):
        feedbackset = mommy.make('devilry_group.Feedbackset', id=10)
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 10)

    def test_group_id(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset = mommy.make('devilry_group.Feedbackset', group=group)
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['group_id'], group.id)

    def test_created_datetime(self):
        feedbackset = mommy.make('devilry_group.Feedbackset', group=mommy.make('core.AssignmentGroup'))
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_datetime'], feedbackset.created_datetime.isoformat())

    def test_feedbackset_type(self):
        feedbackset = mommy.make('devilry_group.Feedbackset',
                                 group=mommy.make('core.AssignmentGroup'),
                                 feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT)
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['feedbackset_type'], feedbackset.feedbackset_type)

    def test_is_last_in_group(self):
        feedbackset = mommy.make('devilry_group.Feedbackset',
                                 group=mommy.make('core.AssignmentGroup'),
                                 is_last_in_group=True)
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['is_last_in_group'], feedbackset.is_last_in_group)

    def test_deadline_datetime_first_attempt(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = mommy.make('devilry_group.Feedbackset',
                                 group=group,
                                 feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT)
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['deadline_datetime'], group.parentnode.first_deadline.isoformat())

    def test_deadline_datetime_new_attempt(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = mommy.make('devilry_group.Feedbackset',
                                 group=group,
                                 feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT)
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['deadline_datetime'], feedbackset.deadline_datetime)

            # def test_anonymized_created_by_fullname_num_queries(self):
    #     group = mommy.make('core.AssignmentGroup',
    #                        parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
    #     candidate = devilry_core_mommy_factories.candidate(group=group)
    #     examiner = devilry_core_mommy_factories.examiner(group=group)
    #     group_mommy.feedbackset_first_attempt_published(is_last_in_group=None,
    #                                                     group=group, created_by=examiner.relatedexaminer.user)
    #     apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
    #     with self.assertNumQueries(1):
    #         self.mock_get_request(apikey=apikey.key)


class TestFeedbacksetAnonymization(api_test_helper.TestCaseMixin,
                                   APITestCase):
    viewclass = feedbackset_student.FeedbacksetViewStudent

    def test_anonymization_off_created_by_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        candidate = devilry_core_mommy_factories.candidate(group=group)
        examiner = devilry_core_mommy_factories.examiner(group=group, fullname='Thor')
        group_mommy.feedbackset_first_attempt_published(is_last_in_group=None,
                                                        group=group, created_by=examiner.relatedexaminer.user)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], 'Thor')

    def test_anonymization_fully_created_by_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        candidate = devilry_core_mommy_factories.candidate(group=group)
        examiner = devilry_core_mommy_factories.examiner(group=group)
        group_mommy.feedbackset_first_attempt_published(is_last_in_group=None,
                                                        group=group, created_by=examiner.relatedexaminer.user)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], 'Anonymous ID missing')

    def test_anonymization_semi_created_by_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = devilry_core_mommy_factories.candidate(group=group)
        examiner = devilry_core_mommy_factories.examiner(group=group)
        group_mommy.feedbackset_first_attempt_published(is_last_in_group=None,
                                                        group=group, created_by=examiner.relatedexaminer.user)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], 'Anonymous ID missing')

    def test_anonymization_off_feedbackset_created_by_admins(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        candidate = devilry_core_mommy_factories.candidate(group=group)
        group_mommy.feedbackset_first_attempt_published(is_last_in_group=None, group=group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], None)

    def test_anonymization_semi_feedbackset_created_by_admins(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = devilry_core_mommy_factories.candidate(group=group)
        group_mommy.feedbackset_first_attempt_published(is_last_in_group=None, group=group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], None)

    def test_anonymization_feedbackset_created_by_admins(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = devilry_core_mommy_factories.candidate(group=group)
        group_mommy.feedbackset_first_attempt_published(is_last_in_group=None, group=group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], None)


class TestFeedbacksetFilters(api_test_helper.TestCaseMixin,
                             APITestCase):
    viewclass = feedbackset_student.FeedbacksetViewStudent

    def test_filter_id_not_found(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(id=10)
        candidate = devilry_core_mommy_factories.candidate(group=feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?id=20')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_id_found(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(id=10)
        candidate = devilry_core_mommy_factories.candidate(group=feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?id=10')
        self.assertEqual(200, response.status_code)
        self.assertEqual(feedbackset.id, response.data[0]['id'])

    def test_filter_group_id_not_found(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__id=10)
        candidate = devilry_core_mommy_factories.candidate(group=feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?group_id=20')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_group_id_found(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__id=10)
        candidate = devilry_core_mommy_factories.candidate(group=feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?group_id=10')
        self.assertEqual(200, response.status_code)
        self.assertEqual(feedbackset.group.id, response.data[0]['group_id'])

    def test_filter_ordering_id_asc(self):
        group = mommy.make('core.AssignmentGroup')
        candidate = devilry_core_mommy_factories.candidate(group=group)
        group_mommy.feedbackset_first_attempt_published(group=group, id=10, is_last_in_group=False)
        group_mommy.feedbackset_new_attempt_unpublished(group=group, id=20, is_last_in_group=True)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?ordering=id')
        self.assertEqual(200, response.status_code)
        self.assertListEqual([feedbackset['id'] for feedbackset in response.data], [10, 20])

    def test_filter_ordering_id_desc(self):
        group = mommy.make('core.AssignmentGroup')
        candidate = devilry_core_mommy_factories.candidate(group=group)
        group_mommy.feedbackset_first_attempt_published(group=group, id=10, is_last_in_group=False)
        group_mommy.feedbackset_new_attempt_unpublished(group=group, id=20, is_last_in_group=True)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?ordering=-id')
        self.assertEqual(200, response.status_code)
        self.assertListEqual([feedbackset['id'] for feedbackset in response.data], [20, 10])
