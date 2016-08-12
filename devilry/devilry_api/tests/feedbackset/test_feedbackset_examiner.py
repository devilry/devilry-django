# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.apps.core import devilry_core_mommy_factories
from devilry.devilry_api import devilry_api_mommy_factories
from devilry.devilry_api.feedbackset.views import feedbackset_examiner
from devilry.devilry_api.tests.mixins import test_examiner_mixins, api_test_helper, test_common_mixins
from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.apps.core import mommy_recipes


class TestFeedbacksetSanity(test_common_mixins.TestReadOnlyPermissionMixin,
                            test_examiner_mixins.TestAuthAPIKeyExaminerMixin,
                            api_test_helper.TestCaseMixin,
                            APITestCase):
    viewclass = feedbackset_examiner.FeedbacksetListViewExaminer

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


class TestFeedbacksetPost(api_test_helper.TestCaseMixin,
                          APITestCase):
    viewclass = feedbackset_examiner.FeedbacksetListViewExaminer

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
                           id=10,
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = mommy.make('core.Examiner')
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            data={
                'group_id': 10,
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
