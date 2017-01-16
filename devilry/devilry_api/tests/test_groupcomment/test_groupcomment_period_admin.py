from model_mommy import mommy
from rest_framework.test import APITestCase


from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.devilry_api import devilry_api_mommy_factories as api_mommy
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_api.tests.mixins import test_admin_mixins, api_test_helper, test_common_mixins
from devilry.devilry_api.group_comment.views.groupcomment_period_admin import GroupCommentViewPeriodAdmin
from devilry.devilry_group.models import GroupComment
from devilry.apps.core.models import Assignment


class TestGroupCommentSanity(test_common_mixins.TestReadOnlyPermissionMixin,
                             test_admin_mixins.TestAuthAPIKeyAdminMixin,
                             api_test_helper.TestCaseMixin,
                             APITestCase):
    viewclass = GroupCommentViewPeriodAdmin

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_anonymization_mode_semi_no_access(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_anonymization_mode_fully_no_access(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_not_part_of_period(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period'))
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_sanity(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 1)

    def test_published_datetime(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        comment = mommy.make('devilry_group.GroupComment',
                             visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                             feedback_set=feedbackset,
                             user_role=GroupComment.USER_ROLE_EXAMINER,
                             comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['published_datetime'], comment.published_datetime)

    def test_text(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   text='lol')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['text'], 'lol')

    def test_id(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   id=20)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 20)

    def test_visible_to_everyone(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['visibility'], GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

    def test_part_of_grading(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertFalse(response.data[0]['part_of_grading'])

    def test_user_fullname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group, fullname='Thor')
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   feedback_set=feedbackset,
                   user=examiner.relatedexaminer.user,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['user_fullname'], 'Thor')

    def test_user_shortname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group, shortname='Thor@example.com')
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   feedback_set=feedbackset,
                   user=examiner.relatedexaminer.user,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['user_shortname'], 'Thor@example.com')

    def test_user_role(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['user_role'], GroupComment.USER_ROLE_STUDENT)

    def test_num_queries(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        for index in range(100):
            mommy.make('devilry_group.GroupComment',
                       visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                       user=period_admin.user,
                       feedback_set=feedbackset,
                       user_role=GroupComment.USER_ROLE_ADMIN,
                       comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        with self.assertNumQueries(2):
            self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)

class TestGroupCommentVisibility(api_test_helper.TestCaseMixin,
                                 APITestCase):
    viewclass = GroupCommentViewPeriodAdmin

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_visible_to_examiners_and_admins_by_examiner(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   id=40)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 40)

    def test_visible_to_examiners_and_admins_by_request_user_period_admin(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_ADMIN,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   id=40,
                   user=period_admin.user)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 40)

    def test_visible_to_examiners_and_admins_by_another_period_admin(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_ADMIN,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   id=40)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 40)

    def test_visible_to_everyone_created_by_student(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   id=30)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 30)

    def test_cannot_see_examiner_draft_comment(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_PRIVATE,
                   feedback_set=feedbackset,
                   part_of_grading=True,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)


class TestGroupCommentPeriodAdminPost(api_test_helper.TestCaseMixin,
                                      APITestCase):
    viewclass = GroupCommentViewPeriodAdmin

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_unauthorized_401(self):
        response = self.mock_post_request(feedbackset=1)
        self.assertEqual(401, response.status_code)

    def test_period_admin_not_part_of_period(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period'))
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            feedback_set=feedbackset.id,
            data={
                'text': 'heia'
            })
        self.assertEqual(403, response.status_code)
        self.assertEqual(response.data['detail'], 'Access denied Period admin does not have access to feedbackset')

    def test_period_admin_cannot_post_part_of_grading_comments_visibility_private(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            feedback_set=feedbackset.id,
            data={
                'text': 'heia',
                'visibility': GroupComment.VISIBILITY_PRIVATE
            })
        self.assertEqual(400, response.status_code)
        self.assertEqual(response.data['non_field_errors'][0], 'Period admin cannot post part of grading comments')

    def test_period_admin_cannot_post_part_of_grading_comments_part_of_grading_true(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            feedback_set=feedbackset.id,
            data={
                'text': 'heia',
                'part_of_grading': True
            })
        self.assertEqual(400, response.status_code)
        self.assertEqual(response.data['non_field_errors'][0], 'Period admin cannot post part of grading comments')

    def test_period_admin_user_role_cannot_be_student(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            feedback_set=feedbackset.id,
            data={
                'text': 'heia',
                'user_role': GroupComment.USER_ROLE_STUDENT
            })
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['user_role'], GroupComment.USER_ROLE_ADMIN)

    def test_period_admin_user_role_cannot_be_examiner(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            feedback_set=feedbackset.id,
            data={
                'text': 'heia',
                'user_role': GroupComment.USER_ROLE_EXAMINER
            })
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['user_role'], GroupComment.USER_ROLE_ADMIN)

    def test_period_admin_post_comment_visibile_to_examiners_and_admins(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            feedback_set=feedbackset.id,
            data={
                'text': 'heia',
                'visibility': GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS
            })
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['visibility'], GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)

    def test_period_admin_post_comment_visibile_to_everyone(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            feedback_set=feedbackset.id,
            data={
                'text': 'heia',
                'visibility': GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
            })
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['visibility'], GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

    def test_post_comment_sanity(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            feedback_set=feedbackset.id,
            data={
                'text': 'heia',
                'visibility': GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
            })
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['visibility'], GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEqual(response.data['text'], 'heia')
        self.assertEqual(response.data['user_role'], GroupComment.USER_ROLE_ADMIN)
        self.assertEqual(response.data['feedback_set'], feedbackset.id)
        self.assertFalse(response.data['part_of_grading'])
        self.assertEqual(response.data['user_fullname'], 'Admin')

    def test_post_comment_created_in_db(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(
            apikey=apikey.key,
            feedback_set=feedbackset.id,
            data={
                'text': 'heia',
                'visibility': GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
            })
        self.assertEqual(201, response.status_code)
        comment = GroupComment.objects.get(id=response.data['id'])
        self.assertEqual(comment.text, 'heia')
        self.assertEqual(comment.visibility, GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEqual(comment.user_role, GroupComment.USER_ROLE_ADMIN)
        self.assertEqual(comment.user_id, period_admin.user.id)
        self.assertEqual(comment.feedback_set.id, feedbackset.id)
        self.assertFalse(comment.part_of_grading)

    def test_num_queries(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        with self.assertNumQueries(6):
            response = self.mock_post_request(
                apikey=apikey.key,
                feedback_set=feedbackset.id,
                data={
                    'text': 'heia',
                    'visibility': GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                })
        self.assertEqual(201, response.status_code)
