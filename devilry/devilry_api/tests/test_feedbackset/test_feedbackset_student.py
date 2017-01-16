# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from model_mommy import mommy
from rest_framework.test import APITestCase

from django.conf import settings
from devilry.apps.core import devilry_core_mommy_factories
from devilry.apps.core.models import Assignment
from devilry.devilry_api import devilry_api_mommy_factories
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_api.feedbackset.views import feedbackset_student
from devilry.devilry_api.tests.mixins import test_student_mixins, api_test_helper, test_common_mixins
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group.models import FeedbackSet


class TestFeedbacksetSanity(test_common_mixins.TestReadOnlyPermissionMixin,
                            test_student_mixins.TestAuthAPIKeyStudentMixin,
                            api_test_helper.TestCaseMixin,
                            APITestCase):
    viewclass = feedbackset_student.FeedbacksetViewStudent

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_sanity(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)

    def test_id(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], feedbackset.id)

    def test_group_id(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['group_id'], feedbackset.group.id)

    def test_created_datetime(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_datetime'], feedbackset.created_datetime.isoformat())

    def test_feedbackset_type(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['feedbackset_type'], feedbackset.feedbackset_type)

    def test_deadline_datetime_first_attempt(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['deadline_datetime'], feedbackset.group.parentnode.first_deadline.isoformat())

    def test_deadline_datetime_new_attempt(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_new_attempt_unpublished(
            group=group,
            id=group.cached_data.last_feedbackset.id + 1
        )
        candidate = devilry_core_mommy_factories.candidate(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(
            apikey=apikey.key,
            queryparams='?id={}'.format(group.cached_data.last_feedbackset.id+1)
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['deadline_datetime'], feedbackset.deadline_datetime.isoformat())

    def test_multiple_groups_and_feedbacksets(self):
        assignment1 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        assignment2 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        related_student = mommy.make('core.RelatedStudent', user=testuser)
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment1)
        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment2)
        mommy.make('core.Candidate', assignment_group=group1, relatedstudent=related_student)
        mommy.make('core.Candidate', assignment_group=group2, relatedstudent=related_student)
        group_mommy.feedbackset_first_attempt_published(group=group1)
        group_mommy.feedbackset_first_attempt_published(group=group2)
        group_mommy.feedbackset_new_attempt_unpublished(group=group1)
        group_mommy.feedbackset_new_attempt_unpublished(group=group2)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=testuser)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(len(response.data), 4)

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

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_anonymization_off_created_by_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        candidate = devilry_core_mommy_factories.candidate(group=group)
        examiner = devilry_core_mommy_factories.examiner(group=group, fullname='Thor')
        group_mommy.feedbackset_first_attempt_published(group=group, created_by=examiner.relatedexaminer.user)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], 'Thor')

    def test_anonymization_fully_created_by_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        candidate = devilry_core_mommy_factories.candidate(group=group)
        examiner = devilry_core_mommy_factories.examiner(group=group)
        group_mommy.feedbackset_first_attempt_published(group=group, created_by=examiner.relatedexaminer.user)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], 'Anonymous ID missing')

    def test_anonymization_semi_created_by_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = devilry_core_mommy_factories.candidate(group=group)
        examiner = devilry_core_mommy_factories.examiner(group=group)
        group_mommy.feedbackset_first_attempt_published(group=group, created_by=examiner.relatedexaminer.user)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], 'Anonymous ID missing')

    def test_anonymization_off_feedbackset_created_by_admins(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        candidate = devilry_core_mommy_factories.candidate(group=group)
        group_mommy.feedbackset_first_attempt_published(group=group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], None)

    def test_anonymization_semi_feedbackset_created_by_admins(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = devilry_core_mommy_factories.candidate(group=group)
        group_mommy.feedbackset_first_attempt_published(group=group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], None)

    def test_anonymization_feedbackset_created_by_admins(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = devilry_core_mommy_factories.candidate(group=group)
        group_mommy.feedbackset_first_attempt_published(group=group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], None)

    # def test_num_queries(self):
    #     testuser = mommy.make(settings.AUTH_USER_MODEL)
    #     related_student = mommy.make('core.RelatedStudent', user=testuser)
    #     group1 = mommy.make('core.AssignmentGroup')
    #     group2 = mommy.make('core.AssignmentGroup')
    #     mommy.make('core.Candidate', assignment_group=group1, relatedstudent=related_student)
    #     mommy.make('core.Candidate', assignment_group=group2, relatedstudent=related_student)
    #     group_mommy.feedbackset_first_attempt_published(is_last_in_group=False, group=group1)
    #     group_mommy.feedbackset_first_attempt_published(is_last_in_group=False, group=group2)
    #     group_mommy.feedbackset_new_attempt_unpublished(group=group1)
    #     group_mommy.feedbackset_new_attempt_unpublished(group=group2)
    #     apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=testuser)
    #     with self.assertNumQueries(3):
    #         self.mock_get_request(apikey=apikey.key)


class TestFeedbacksetFilters(api_test_helper.TestCaseMixin,
                             APITestCase):
    viewclass = feedbackset_student.FeedbacksetViewStudent

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_filter_id_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group=feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?id={}'.format(feedbackset.id+1))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_id_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group=feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?id={}'.format(feedbackset.id))
        self.assertEqual(200, response.status_code)
        self.assertEqual(feedbackset.id, response.data[0]['id'])

    def test_filter_group_id_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', id=10, parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        candidate = devilry_core_mommy_factories.candidate(group=feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?group_id=20')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_group_id_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', id=10, parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        candidate = devilry_core_mommy_factories.candidate(group=feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?group_id=10')
        self.assertEqual(200, response.status_code)
        self.assertEqual(feedbackset.group.id, response.data[0]['group_id'])

    def test_filter_ordering_id_asc(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group=group)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=group)
        group_mommy.feedbackset_new_attempt_unpublished(group=group, id=testfeedbackset.id + 1)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?ordering=id')
        self.assertEqual(200, response.status_code)
        self.assertListEqual(
            [feedbackset['id'] for feedbackset in response.data], [testfeedbackset.id, testfeedbackset.id + 1]
        )

    def test_filter_ordering_id_desc(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group=group)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=group)
        group_mommy.feedbackset_new_attempt_unpublished(group=group, id=testfeedbackset.id + 1)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?ordering=-id')
        self.assertEqual(200, response.status_code)
        self.assertListEqual(
            [feedbackset['id'] for feedbackset in response.data], [testfeedbackset.id + 1, testfeedbackset.id]
        )