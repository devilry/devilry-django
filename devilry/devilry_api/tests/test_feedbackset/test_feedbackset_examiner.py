# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from model_mommy import mommy
from rest_framework.test import APITestCase
from django.conf import settings

from devilry.apps.core import devilry_core_mommy_factories
from devilry.devilry_api import devilry_api_mommy_factories
from devilry.devilry_api.feedbackset.views import feedbackset_examiner
from devilry.devilry_api.tests.mixins import test_examiner_mixins, api_test_helper, test_common_mixins
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.apps.core import mommy_recipes
from devilry.apps.core.models import Assignment


class TestFeedbacksetSanity(test_common_mixins.TestReadOnlyPermissionMixin,
                            test_examiner_mixins.TestAuthAPIKeyExaminerMixin,
                            api_test_helper.TestCaseMixin,
                            APITestCase):
    viewclass = feedbackset_examiner.FeedbacksetViewExaminer

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_sanity(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.data))

    def test_id(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_new_attempt_unpublished(group=group)
        examiner = devilry_core_mommy_factories.examiner(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], feedbackset.id)

    def test_group_id(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment, group__id=15)
        examiner = devilry_core_mommy_factories.examiner(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['group_id'], feedbackset.group.id)

    def test_created_datetime(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_datetime'], feedbackset.created_datetime.isoformat())

    def test_feedbackset_type(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['feedbackset_type'], feedbackset.feedbackset_type)

    def test_deadline_datetime_first_attempt(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['deadline_datetime'], assignment.first_deadline.isoformat())

    def test_deadline_datetime_new_attempt(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_new_attempt_unpublished(
            group=group, id=group.cached_data.last_feedbackset.id+1)
        examiner = devilry_core_mommy_factories.examiner(group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(
            apikey=apikey.key,
            queryparams='?id={}'.format(group.cached_data.last_feedbackset.id+1))
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['deadline_datetime'], feedbackset.deadline_datetime.isoformat())

    def test_created_by_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        group_mommy.feedbackset_first_attempt_unpublished(group=group, created_by=examiner.relatedexaminer.user)
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
        group_mommy.feedbackset_first_attempt_published(group=group1)
        group_mommy.feedbackset_first_attempt_published(group=group2)
        group_mommy.feedbackset_new_attempt_unpublished(group=group1)
        group_mommy.feedbackset_new_attempt_unpublished(group=group2)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=testuser)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(len(response.data), 4)

    # def test_num_queries(self):
    #     testuser = mommy.make(settings.AUTH_USER_MODEL)
    #     related_examiner = mommy.make('core.RelatedExaminer', user=testuser)
    #     apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=testuser)
    #
    #     for index in range(100):
    #         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
    #         feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
    #         mommy.make('core.Examiner', assignmentgroup=feedbackset.group, relatedexaminer=related_examiner)
    #     with self.assertNumQueries(10):
    #         self.mock_get_request(apikey=apikey.key)



class TestFeedbacksetAnonymization(api_test_helper.TestCaseMixin,
                                   APITestCase):
    viewclass = feedbackset_examiner.FeedbacksetViewExaminer

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_anonymization_off_new_feedbackset_created_by_another_examiner(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, fullname='Donald')
        request_examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group=group,
            created_by=examiner.relatedexaminer.user
        )
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(
            user=request_examiner.relatedexaminer.user
        )
        response = self.mock_get_request(
            apikey=apikey.key,
            queryparam='?id={}'.format(feedbackset.id)
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], 'Donald')

    def test_anonymization_semi_new_feedbackset_created_by_another_examiner(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, fullname='Donald')
        request_examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group=group,
            created_by=examiner.relatedexaminer.user
        )
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(
            user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(
            apikey=apikey.key,
            queryparam='?id={}'.format(feedbackset.id)
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], 'Donald')

    def test_anonymization_fully_new_feedbackset_created_by_another_examiner(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, fullname='Donald')
        request_examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group=group,
            created_by=examiner.relatedexaminer.user
        )
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(
            user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(
            apikey=apikey.key,
            queryparam='?id={}'.format(feedbackset.id)
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], 'Donald')

    def test_feeedbackset_anonymization_off_first(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        request_examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(
            user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], None)

    def test_feeedbackset_anonymization_semi_first(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        request_examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(
            user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], None)

    def test_feeedbackset_anonymization_fully_first(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        request_examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(
            user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_by_fullname'], None)


class TestFeedbacksetFilters(api_test_helper.TestCaseMixin,
                             APITestCase):
    viewclass = feedbackset_examiner.FeedbacksetViewExaminer

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_filter_id_not_found(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = devilry_core_mommy_factories.examiner(group=feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?id={}'.format(feedbackset.id+1))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_id_found(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = devilry_core_mommy_factories.examiner(group=feedbackset.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?id={}'.format(feedbackset.id))
        self.assertEqual(200, response.status_code)
        self.assertEqual(feedbackset.id, response.data[0]['id'])

    def test_filter_group_id_not_found(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'),
                           id=10)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
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
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=group)
        group_mommy.feedbackset_new_attempt_unpublished(group=group, id=testfeedbackset.id+1)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?ordering=id')
        self.assertEqual(200, response.status_code)
        self.assertListEqual([feedbackset['id'] for feedbackset in response.data], [testfeedbackset.id, testfeedbackset.id+1])

    def test_filter_ordering_id_desc(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        examiner = devilry_core_mommy_factories.examiner(group=group)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=group)
        group_mommy.feedbackset_new_attempt_unpublished(group=group, id=testfeedbackset.id+1)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?ordering=-id')
        self.assertEqual(200, response.status_code)
        self.assertListEqual([feedbackset['id'] for feedbackset in response.data], [testfeedbackset.id+1, testfeedbackset.id])


class TestFeedbacksetPost(api_test_helper.TestCaseMixin,
                          APITestCase):
    viewclass = feedbackset_examiner.FeedbacksetViewExaminer

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

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
        self.assertEqual(response.data['created_by_fullname'], examiner.relatedexaminer.user.fullname)


class TestFeedbacksetPatchPublishFeedbackset(api_test_helper.TestCaseMixin, APITestCase):
    viewclass = feedbackset_examiner.FeedbacksetViewExaminer

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_unauthorized_401(self):
        response = self.mock_patch_request()
        self.assertEqual(401, response.status_code)

    def test_publish_feedbackset_id_missing(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = devilry_core_mommy_factories.examiner(group, fullname="Tor med hammern")
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_patch_request(
            apikey=apikey.key)
        self.assertEqual(400, response.status_code)
        self.assertEqual(response.data['detail'], 'query parameter "id" required')

    def test_publish_feedbackset_grading_points_missing(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = devilry_core_mommy_factories.examiner(group, fullname="Tor med hammern")
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_patch_request(
            apikey=apikey.key,
            queryparams='?id={}'.format(feedbackset.id))
        self.assertEqual(400, response.status_code)

    def test_publish_feedbackset_not_part_of_group_404(self):
        group1 = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        group2 = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset1 = group_mommy.feedbackset_first_attempt_unpublished(group=group1)
        feedbackset2 = group_mommy.feedbackset_first_attempt_unpublished(group=group2)
        examiner = devilry_core_mommy_factories.examiner(feedbackset2.group, fullname="Tor med hammern")
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_patch_request(
            apikey=apikey.key,
            queryparams='?id={}&grading_points=1'.format(feedbackset1.id))
        self.assertEqual(404, response.status_code)

    def test_publish_feedbackset_sanity(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = devilry_core_mommy_factories.examiner(group, fullname="Tor med hammern")
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_patch_request(
            apikey=apikey.key,
            queryparams='?id={}&grading_points=1'.format(feedbackset.id))
        self.assertEqual(200, response.status_code)
        feedbackset = FeedbackSet.objects.get(id=feedbackset.id)
        self.assertEqual(feedbackset.grading_published_by, examiner.relatedexaminer.user)
        self.assertEqual(feedbackset.grading_points, 1)
        self.assertIsNotNone(feedbackset.grading_published_datetime)
