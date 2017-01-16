from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.devilry_api import devilry_api_mommy_factories as api_mommy
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_api.tests.mixins import test_admin_mixins, api_test_helper, test_common_mixins
from devilry.devilry_api.feedbackset.views.feedbackset_period_admin import FeedbacksetViewPeriodAdmin
from devilry.devilry_group.models import FeedbackSet
from devilry.apps.core.models import Assignment


class TestFeedbacksetSanity(test_common_mixins.TestReadOnlyPermissionMixin,
                            test_admin_mixins.TestAuthAPIKeyAdminMixin,
                            api_test_helper.TestCaseMixin,
                            APITestCase):
    viewclass = FeedbacksetViewPeriodAdmin

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_anonymization_mode_semi_anonymous_no_access(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_anonymization_mode_fully_anonymous_no_access(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_not_part_of_period(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period'))
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_sanity(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 1)

    def test_group_id(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['group_id'], group.id)

    def test_created_datetime(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_datetime'], feedbackset.created_datetime.isoformat())

    def test_deadline_datetime_first_attempt(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['deadline_datetime'], group.parentnode.first_deadline.isoformat())

    def test_deadline_datetime_new_attempt(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        feedbackset = group_mommy.feedbackset_new_attempt_unpublished(group=group)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key, queryparam="?id={}".format(feedbackset.id))
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['deadline_datetime'], feedbackset.deadline_datetime.isoformat())


class TestFeedbacksetFilters(api_test_helper.TestCaseMixin,
                             APITestCase):
    viewclass = FeedbacksetViewPeriodAdmin

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_filter_id_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?id={}'.format(feedbackset.id+1))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_id_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?id={}'.format(feedbackset.id))
        self.assertEqual(200, response.status_code)
        self.assertEqual(feedbackset.id, response.data[0]['id'])

    def test_filter_group_id_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', id=10, parentnode=assignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?group_id=20')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_group_id_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', id=10, parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?group_id=10')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['group_id'], feedbackset.group.id)

    def test_filter_ordering_id_asc(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset1 = group_mommy.feedbackset_first_attempt_published(group=group)
        feedbackset2 = group_mommy.feedbackset_new_attempt_unpublished(group=group, id=feedbackset1.id+1)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?ordering=id')
        self.assertEqual(200, response.status_code)
        self.assertListEqual([feedbackset['id'] for feedbackset in response.data], [feedbackset1.id, feedbackset2.id])

    def test_filter_ordering_id_desc(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset1 = group_mommy.feedbackset_first_attempt_published(group=group)
        feedbackset2 = group_mommy.feedbackset_new_attempt_unpublished(group=group, id=feedbackset1.id + 1)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?ordering=-id')
        self.assertEqual(200, response.status_code)
        self.assertListEqual([feedbackset['id'] for feedbackset in response.data], [feedbackset2.id, feedbackset1.id])

#
# class TestFeedbacksetPost(api_test_helper.TestCaseMixin,
#                           APITestCase):
#     viewclass = FeedbacksetViewPeriodAdmin
#
#     def test_post_no_data(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_post_request(apikey=apikey.key)
#         self.assertEqual(400, response.status_code)
#
#     def test_post_group_id_missing(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_post_request(
#             apikey=apikey.key,
#             data={
#                 'deadline_datetime': mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE,
#                 'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
#             })
#         self.assertEqual(400, response.status_code)
#         self.assertEqual(['This field is required.'], response.data['group_id'])
#
#     def test_post_deadline_datetime_missing(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         group = mommy.make('core.AssignmentGroup', parentnode=assignment)
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_post_request(
#             apikey=apikey.key,
#             data={
#                 'group_id': group.id,
#                 'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
#             })
#         self.assertEqual(400, response.status_code)
#         self.assertEqual(['This field is required.'], response.data['deadline_datetime'])
#
#     def test_post_deadline_feedbackset_type_missing(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         group = mommy.make('core.AssignmentGroup', parentnode=assignment)
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_post_request(
#             apikey=apikey.key,
#             data={
#                 'group_id': group.id,
#                 'deadline_datetime': mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE
#             })
#         self.assertEqual(400, response.status_code)
#         self.assertEqual(['This field is required.'], response.data['feedbackset_type'])
#
#     def test_post_deadline_in_past(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         group = mommy.make('core.AssignmentGroup', parentnode=assignment)
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_post_request(
#             apikey=apikey.key,
#             data={
#                 'group_id': group.id,
#                 'deadline_datetime': mommy_recipes.ASSIGNMENT_OLDPERIOD_START_FIRST_DEADLINE,
#                 'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
#             })
#         self.assertEqual(400, response.status_code)
#         self.assertEqual(['Deadline must be in the future'], response.data['deadline_datetime'])
#
#     def test_post_period_admin_not_part_of_period(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         group = mommy.make('core.AssignmentGroup', parentnode=assignment)
#         period_admin = core_mommy.period_admin(period=mommy.make('core.Period'))
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_post_request(
#             apikey=apikey.key,
#             data={
#                 'group_id': group.id,
#                 'deadline_datetime': mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE,
#                 'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
#             })
#         self.assertEqual(400, response.status_code)
#         self.assertEqual(['Access denied Period admin not part of period'], response.data['group_id'])
#
#     def test_post_anonymization_mode_semi_access_denied(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
#                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
#         group = mommy.make('core.AssignmentGroup', parentnode=assignment)
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_post_request(
#             apikey=apikey.key,
#             data={
#                 'group_id': group.id,
#                 'deadline_datetime': mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE,
#                 'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
#             })
#         self.assertEqual(400, response.status_code)
#         self.assertEqual(['Access denied Period admin not part of period'], response.data['group_id'])
#
#     def test_post_anonymization_mode_fully_access_denied(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
#                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
#         group = mommy.make('core.AssignmentGroup', parentnode=assignment)
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_post_request(
#             apikey=apikey.key,
#             data={
#                 'group_id': group.id,
#                 'deadline_datetime': mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE,
#                 'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
#             })
#         self.assertEqual(400, response.status_code)
#         self.assertEqual(['Access denied Period admin not part of period'], response.data['group_id'])
#
#     def test_feedbackset_type_first_attempt(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         group = mommy.make('core.AssignmentGroup', parentnode=assignment)
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_post_request(
#             apikey=apikey.key,
#             data={
#                 'group_id': group.id,
#                 'deadline_datetime': mommy_recipes.ASSIGNMENT_OLDPERIOD_START_FIRST_DEADLINE,
#                 'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT
#             })
#         self.assertEqual(400, response.status_code)
#
#     def test_previous_feedbackset_is_last_in_group_false(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         group = mommy.make('core.AssignmentGroup', parentnode=assignment)
#         prev_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         self.assertTrue(prev_feedbackset.is_last_in_group)
#         response = self.mock_post_request(
#             apikey=apikey.key,
#             data={
#                 'group_id': group.id,
#                 'deadline_datetime': mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE,
#                 'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
#             })
#         self.assertEqual(201, response.status_code)
#         feedbackset = FeedbackSet.objects.get(id=prev_feedbackset.id)
#         self.assertFalse(feedbackset.is_last_in_group)
#
#     def test_post_exist_in_db(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         group = mommy.make('core.AssignmentGroup', parentnode=assignment)
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_post_request(
#             apikey=apikey.key,
#             data={
#                 'group_id': group.id,
#                 'deadline_datetime': mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE,
#                 'feedbackset_type': FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT
#             })
#         self.assertEqual(201, response.status_code)
#         feedbackset = FeedbackSet.objects.get(id=response.data['id'])
#         self.assertEqual(response.data['feedbackset_type'], feedbackset.feedbackset_type)
#         self.assertEqual(response.data['group_id'], feedbackset.group.id)
#         self.assertEqual(response.data['deadline_datetime'], feedbackset.current_deadline().isoformat())
#         self.assertEqual(response.data['created_datetime'], feedbackset.created_datetime.isoformat())
#         self.assertEqual(response.data['is_last_in_group'], feedbackset.is_last_in_group)
#         self.assertEqual(response.data['created_by_fullname'], None)
#
#
# class TestFeedbacksetPatchPublishFeedbackset(api_test_helper.TestCaseMixin, APITestCase):
#     viewclass = FeedbacksetViewPeriodAdmin
#
#     def test_unauthorized_401(self):
#         response = self.mock_patch_request()
#         self.assertEqual(401, response.status_code)
#
#     def test_publish_feedbackset_id_missing(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         group = mommy.make('core.AssignmentGroup', parentnode=assignment)
#         group_mommy.feedbackset_first_attempt_unpublished(id=11, group=group)
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_patch_request(
#             apikey=apikey.key)
#         self.assertEqual(400, response.status_code)
#         self.assertEqual(response.data['detail'], 'query parameter "id" required')
#
#     def test_publish_feedbackset_grading_points_missing(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         group = mommy.make('core.AssignmentGroup', parentnode=assignment)
#         group_mommy.feedbackset_first_attempt_unpublished(id=11, group=group)
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_patch_request(
#             apikey=apikey.key,
#             queryparams='?id=11')
#         self.assertEqual(400, response.status_code)
#
#     def test_publish_feedbackset_not_part_of_period_404(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         group = mommy.make('core.AssignmentGroup', parentnode=assignment)
#         group_mommy.feedbackset_first_attempt_unpublished(id=11, group=group)
#         period_admin = core_mommy.period_admin(period=mommy.make('core.Period'))
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_patch_request(
#             apikey=apikey.key,
#             queryparams='?id=11&grading_points=1')
#         self.assertEqual(404, response.status_code)
#
#     def test_publish_feedbackset_sanity(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#         group = mommy.make('core.AssignmentGroup', parentnode=assignment)
#         group_mommy.feedbackset_first_attempt_unpublished(id=11, group=group)
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_patch_request(
#             apikey=apikey.key,
#             queryparams='?id=11&grading_points=1')
#         self.assertEqual(200, response.status_code)
#         feedbackset = FeedbackSet.objects.get(id=11)
#         self.assertEqual(feedbackset.grading_published_by, period_admin.user)
#         self.assertEqual(feedbackset.grading_points, 1)
#         self.assertIsNotNone(feedbackset.grading_published_datetime)
