# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from model_mommy import mommy
from rest_framework.test import APITestCase
from django.conf import settings

from devilry.apps.core import devilry_core_mommy_factories
from devilry.devilry_api import devilry_api_mommy_factories
from devilry.devilry_api.feedbackset.views import feedbackset_examiner
from devilry.devilry_api.tests.mixins import test_examiner_mixins, api_test_helper, test_common_mixins
from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.apps.core import mommy_recipes
from devilry.apps.core.models import Assignment


class TestFeedbacksetSanity(test_common_mixins.TestReadOnlyPermissionMixin,
                            test_examiner_mixins.TestAuthAPIKeyExaminerMixin,
                            api_test_helper.TestCaseMixin,
                            APITestCase):
    viewclass = feedbackset_examiner.FeedbacksetViewExaminer

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_sanity(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        set = mommy.make('devilry_group.Feedbackset', group=group)
        examiner = devilry_core_mommy_factories.examiner(set.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)

    def test_id(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = mommy.make('devilry_group.Feedbackset', id=10, group=group)
        examiner = devilry_core_mommy_factories.examiner(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 10)

    def test_group_id(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = mommy.make('devilry_group.Feedbackset', group=group)
        examiner = devilry_core_mommy_factories.examiner(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['group_id'], group.id)

    def test_created_datetime(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = mommy.make('devilry_group.Feedbackset', group=group)
        examiner = devilry_core_mommy_factories.examiner(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_datetime'], feedbackset.created_datetime.isoformat())

    def test_feedbackset_type(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = mommy.make('devilry_group.Feedbackset',
                                 group=group,
                                 feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT)
        examiner = devilry_core_mommy_factories.examiner(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['feedbackset_type'], feedbackset.feedbackset_type)

    def test_is_last_in_group(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = mommy.make('devilry_group.Feedbackset',
                                 group=group,
                                 is_last_in_group=True)
        examiner = devilry_core_mommy_factories.examiner(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['is_last_in_group'], feedbackset.is_last_in_group)

    def test_deadline_datetime_first_attempt(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = mommy.make('devilry_group.Feedbackset',
                                 group=group,
                                 feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT)
        examiner = devilry_core_mommy_factories.examiner(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['deadline_datetime'], group.parentnode.first_deadline.isoformat())

    def test_deadline_datetime_new_attempt(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = mommy.make('devilry_group.Feedbackset',
                                 group=group,
                                 feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT)
        examiner = devilry_core_mommy_factories.examiner(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['deadline_datetime'], feedbackset.deadline_datetime)

    def test_created_by_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        mommy.make('devilry_group.Feedbackset', group=group, created_by=examiner.relatedexaminer.user)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], 'Thor')

    def test_multiple_groups_and_feedbacksets(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        related_examiner = mommy.make('core.RelatedExaminer', user=testuser)
        group1 = mommy.make('core.AssignmentGroup',
                            parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        group2 = mommy.make('core.AssignmentGroup',
                            parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        mommy.make('core.Examiner', assignmentgroup=group1, relatedexaminer=related_examiner)
        mommy.make('core.Examiner', assignmentgroup=group2, relatedexaminer=related_examiner)
        group_mommy.feedbackset_first_attempt_published(is_last_in_group=False, group=group1)
        group_mommy.feedbackset_first_attempt_published(is_last_in_group=False, group=group2)
        group_mommy.feedbackset_new_attempt_unpublished(group=group1)
        group_mommy.feedbackset_new_attempt_unpublished(group=group2)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=testuser)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(len(response.data), 4)


class TestFeedbacksetAnonymization(api_test_helper.TestCaseMixin,
                                   APITestCase):
    viewclass = feedbackset_examiner.FeedbacksetViewExaminer

    def test_anonymization_off(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF))
        examiner = devilry_core_mommy_factories.examiner(group, fullname='Donald')
        request_examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        mommy.make('devilry_group.Feedbackset', group=group, created_by=examiner.relatedexaminer.user)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(
            user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], 'Donald')

    def test_anonymization_semi(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
        examiner = devilry_core_mommy_factories.examiner(group, fullname='Donald')
        request_examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        mommy.make('devilry_group.Feedbackset', group=group, created_by=examiner.relatedexaminer.user)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(
            user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], 'Donald')

    def test_anonymization_fully(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        examiner = devilry_core_mommy_factories.examiner(group, fullname='Donald')
        request_examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        mommy.make('devilry_group.Feedbackset', group=group, created_by=examiner.relatedexaminer.user)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(
            user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], 'Donald')

    def test_feeedbackset_first_anonymization_off(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF))
        request_examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        mommy.make('devilry_group.Feedbackset', group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(
            user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], None)

    def test_feeedbackset_first__anonymization_semi(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
        request_examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        mommy.make('devilry_group.Feedbackset', group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(
            user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], None)

    def test_feeedbackset_first__anonymization_fully(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        request_examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        mommy.make('devilry_group.Feedbackset', group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(
            user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], None)


class TestFeedbacksetFilters(api_test_helper.TestCaseMixin,
                             APITestCase):
    viewclass = feedbackset_examiner.FeedbacksetViewExaminer

    def test_filter_id_not_found(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(id=10, group=group)
        examiner = devilry_core_mommy_factories.examiner(group=feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?id=20')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_id_found(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(id=10, group=group)
        examiner = devilry_core_mommy_factories.examiner(group=feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?id=10')
        self.assertEqual(200, response.status_code)
        self.assertEqual(feedbackset.id, response.data[0]['id'])

    def test_filter_group_id_not_found(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'),
                           id=10)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(id=10, group=group)
        examiner = devilry_core_mommy_factories.examiner(group=feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?group_id=20')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_group_id_found(self):
        group = mommy.make('core.AssignmentGroup',
                           id=10,
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = devilry_core_mommy_factories.examiner(group=feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?group_id=10')
        self.assertEqual(200, response.status_code)
        self.assertEqual(feedbackset.group.id, response.data[0]['group_id'])

    def test_filter_ordering_id_asc(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = devilry_core_mommy_factories.examiner(group=group)
        group_mommy.feedbackset_first_attempt_published(group=group, id=10, is_last_in_group=False)
        group_mommy.feedbackset_new_attempt_unpublished(group=group, id=20, is_last_in_group=True)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?ordering=id')
        self.assertEqual(200, response.status_code)
        self.assertListEqual([feedbackset['id'] for feedbackset in response.data], [10, 20])

    def test_filter_ordering_id_desc(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = devilry_core_mommy_factories.examiner(group=group)
        group_mommy.feedbackset_first_attempt_published(group=group, id=10, is_last_in_group=False)
        group_mommy.feedbackset_new_attempt_unpublished(group=group, id=20, is_last_in_group=True)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?ordering=-id')
        self.assertEqual(200, response.status_code)
        self.assertListEqual([feedbackset['id'] for feedbackset in response.data], [20, 10])


class TestFeedbacksetPost(api_test_helper.TestCaseMixin,
                          APITestCase):
    viewclass = feedbackset_examiner.FeedbacksetViewExaminer

    def test_post_no_data(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = devilry_core_mommy_factories.examiner(group)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(apikey=apikey.key)
        self.assertEqual(400, response.status_code)

    def test_post_group_id_missing(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = devilry_core_mommy_factories.examiner(group)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            data={
                'deadline_datetime': mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE,
                'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
            })
        self.assertEqual(400, response.status_code)
        self.assertEqual(['This field is required.'], response.data['group_id'])

    def test_post_deadline_datetime_missing(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = devilry_core_mommy_factories.examiner(group)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            data={
                'group_id': group.id,
                'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
            })
        self.assertEqual(400, response.status_code)
        self.assertEqual(['This field is required.'], response.data['deadline_datetime'])

    def test_post_deadline_feedbackset_type_missing(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = devilry_core_mommy_factories.examiner(group)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            data={
                'group_id': group.id,
                'deadline_datetime': mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE
            })
        self.assertEqual(400, response.status_code)
        self.assertEqual(['This field is required.'], response.data['feedbackset_type'])

    def test_post_deadline_in_past(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = devilry_core_mommy_factories.examiner(group)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            data={
                'group_id': group.id,
                'deadline_datetime': mommy_recipes.ASSIGNMENT_OLDPERIOD_START_FIRST_DEADLINE,
                'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
            })
        self.assertEqual(400, response.status_code)
        self.assertEqual(['Deadline must be in the future'], response.data['deadline_datetime'])

    def test_post_examiner_not_part_of_group(self):
        group = mommy.make('core.AssignmentGroup',
                           id=24,
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = mommy.make('core.Examiner')
        group_mommy.feedbackset_first_attempt_published(group=group, is_last_in_group=False)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            data={
                'group_id': 24,
                'deadline_datetime': mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE,
                'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
            })
        self.assertEqual(400, response.status_code)
        self.assertEqual(['Access denied Examiner not part of assignment group'], response.data['group_id'])

    def test_feedbackset_type_first_attempt(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = devilry_core_mommy_factories.examiner(group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            data={
                'group_id': group.id,
                'deadline_datetime': mommy_recipes.ASSIGNMENT_OLDPERIOD_START_FIRST_DEADLINE,
                'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT
            })
        self.assertEqual(400, response.status_code)

    def test_post_feedbackset_success(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = devilry_core_mommy_factories.examiner(group)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            data={
                'group_id': group.id,
                'deadline_datetime': mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE,
                'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
            })
        self.assertEqual(201, response.status_code)

    def test_previous_feedbackset_is_last_in_group_false(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = devilry_core_mommy_factories.examiner(group)
        prev_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        self.assertTrue(prev_feedbackset.is_last_in_group)
        response = self.mock_post_request(
            apikey=apikey.key,
            data={
                'group_id': group.id,
                'deadline_datetime': mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE,
                'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
            })
        self.assertEqual(201, response.status_code)
        feedbackset = FeedbackSet.objects.get(id=prev_feedbackset.id)
        self.assertFalse(feedbackset.is_last_in_group)

    def test_post_exist_in_db(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = devilry_core_mommy_factories.examiner(group)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            data={
                'group_id': group.id,
                'deadline_datetime': mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE,
                'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
            })
        self.assertEqual(201, response.status_code)
        feedbackset = FeedbackSet.objects.get(id=response.data['id'])
        self.assertEqual(response.data['feedbackset_type'], feedbackset.feedbackset_type)
        self.assertEqual(response.data['group_id'], feedbackset.group.id)
        self.assertEqual(response.data['deadline_datetime'], feedbackset.current_deadline().isoformat())
        self.assertEqual(response.data['created_datetime'], feedbackset.created_datetime.isoformat())
        self.assertEqual(response.data['is_last_in_group'], feedbackset.is_last_in_group)
        self.assertEqual(response.data['created_by_fullname'], examiner.relatedexaminer.user.fullname)


class TestFeedbacksetPatchPublishFeedbackset(api_test_helper.TestCaseMixin, APITestCase):
    viewclass = feedbackset_examiner.FeedbacksetViewExaminer

    def test_unauthorized_401(self):
        response = self.mock_patch_request()
        self.assertEqual(401, response.status_code)

    def test_publish_feedbackset_id_missing(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        group_mommy.feedbackset_first_attempt_unpublished(id=11, group=group)
        examiner = devilry_core_mommy_factories.examiner(group, fullname="Tor med hammern")
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_patch_request(
            apikey=apikey.key)
        self.assertEqual(400, response.status_code)
        self.assertEqual(response.data['detail'], 'query parameter "id" required')

    def test_publish_feedbackset_grading_points_missing(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        group_mommy.feedbackset_first_attempt_unpublished(id=11, group=group)
        examiner = devilry_core_mommy_factories.examiner(group, fullname="Tor med hammern")
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_patch_request(
            apikey=apikey.key,
            queryparams='?id=11')
        self.assertEqual(400, response.status_code)

    def test_publish_feedbackset_not_part_of_group_404(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        group_mommy.feedbackset_first_attempt_unpublished(id=11, group=group)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        examiner = devilry_core_mommy_factories.examiner(feedbackset.group, fullname="Tor med hammern")
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_patch_request(
            apikey=apikey.key,
            queryparams='?id=11&grading_points=1')
        self.assertEqual(404, response.status_code)

    def test_publish_feedbackset_sanity(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        group_mommy.feedbackset_first_attempt_unpublished(id=11, group=group)
        examiner = devilry_core_mommy_factories.examiner(group, fullname="Tor med hammern")
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_patch_request(
            apikey=apikey.key,
            queryparams='?id=11&grading_points=1')
        self.assertEqual(200, response.status_code)
        feedbackset = FeedbackSet.objects.get(id=11)
        self.assertEqual(feedbackset.grading_published_by, examiner.relatedexaminer.user)
        self.assertEqual(feedbackset.grading_points, 1)
        self.assertIsNotNone(feedbackset.grading_published_datetime)
