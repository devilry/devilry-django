# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.devilry_api import devilry_api_mommy_factories as api_mommy
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_api.tests.mixins import test_examiner_mixins, api_test_helper, test_common_mixins
from devilry.devilry_api.group_comment.views import groupcomment_examiner
from devilry.devilry_group.models import GroupComment
from devilry.apps.core.models import Assignment

class TestGroupCommentSanity(test_common_mixins.TestReadOnlyPermissionMixin,
                             test_examiner_mixins.TestAuthAPIKeyExaminerMixin,
                             api_test_helper.TestCaseMixin,
                             APITestCase):
    viewclass = groupcomment_examiner.GroupCommentViewExaminer

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_sanity(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 1)

    def test_published_datetime(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        comment = mommy.make('devilry_group.GroupComment',
                             visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                             user=examiner.relatedexaminer.user,
                             feedback_set=feedbackset,
                             user_role=GroupComment.USER_ROLE_STUDENT,
                             comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['published_datetime'], comment.published_datetime)

    def test_text(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   text='lol')
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['text'], 'lol')

    def test_id(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   id=20)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 20)

    def test_visibility(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['visibility'], GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

    def test_part_of_grading(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertFalse(response.data[0]['part_of_grading'])

    def test_user_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group, fullname='Thor')
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['user_fullname'], 'Thor')

    def test_user_shortname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group, shortname='Thor@example.com')
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['user_shortname'], examiner.relatedexaminer.user.shortname)

    def test_user_role(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['user_role'], GroupComment.USER_ROLE_STUDENT)


class TestGroupCommentAnonymization(api_test_helper.TestCaseMixin,
                                    APITestCase):
    viewclass = groupcomment_examiner.GroupCommentViewExaminer

    def test_anonymization_off_student_user_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        candidate = core_mommy.candidate(group=group, fullname='Alice')
        examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(response.data[0]['user_fullname'], 'Alice')

    def test_anonymization_semi_student_user_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        candidate = core_mommy.candidate(group=group, fullname='Alice',
                                         automatic_anonymous_id='some id')
        examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(response.data[0]['user_fullname'], 'some id')

    def test_anonymization_full_student_user_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        candidate = core_mommy.candidate(group=group, fullname='Alice')
        examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(response.data[0]['user_fullname'], 'Anonymous ID missing')

    def test_anonymization_off_student_user_shortname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        candidate = core_mommy.candidate(group=group, shortname='Alice@example.com')
        examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(response.data[0]['user_shortname'], 'Alice@example.com')

    def test_anonymization_semi_student_user_shortname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        candidate = core_mommy.candidate(group=group, shortname='Alice@example.com',
                                         automatic_anonymous_id='some id')
        examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(response.data[0]['user_fullname'], 'some id')

    def test_anonymization_full_student_user_shortname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        candidate = core_mommy.candidate(group=group, shortname='Alice@example.com')
        examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(response.data[0]['user_fullname'], 'Anonymous ID missing')

    def test_anonymization_off_examiner_user_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group, fullname='Thor')
        request_examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(response.data[0]['user_fullname'], 'Thor')

    def test_anonymization_semi_examiner_user_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group, fullname='Thor')
        request_examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(response.data[0]['user_fullname'], 'Thor')

    def test_anonymization_full_examiner_user_fullname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group, fullname='Thor')
        request_examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(response.data[0]['user_fullname'], 'Thor')

    def test_anonymization_off_examiner_user_shortname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group, shortname='Thor@example.com')
        request_examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(response.data[0]['user_shortname'], 'Thor@example.com')

    def test_anonymization_semi_examiner_user_shortname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group, shortname='Thor@example.com')
        request_examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(response.data[0]['user_shortname'], 'Thor@example.com')

    def test_anonymization_full_examiner_user_shortname(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                        anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group, shortname='Thor@example.com')
        request_examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(response.data[0]['user_shortname'], 'Thor@example.com')


class TestGroupCommentVisibility(api_test_helper.TestCaseMixin,
                                 APITestCase):
    viewclass = groupcomment_examiner.GroupCommentViewExaminer

    def test_visible_to_everyone(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        request_examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   id=50,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 50)

    def test_visible_to_everyone_created_by_student(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        candidate = core_mommy.candidate(group=group)
        request_examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   id=50,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 50)

    def test_visible_private_created_by_requestuser(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        request_examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   id=50,
                   visibility=GroupComment.VISIBILITY_PRIVATE,
                   part_of_grading=True,
                   user=request_examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 50)

    def test_visible_private_created_by_another_examiner(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        request_examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_PRIVATE,
                   part_of_grading=True,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_visible_to_examiner_and_admins_created_by_requestuser(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        request_examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   id=50,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   user=request_examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 50)

    def test_visible_to_examiner_and_admins_created_by_another_examiner(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        request_examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   id=50,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=request_examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 50)


class TestGroupCommentFilters(api_test_helper.TestCaseMixin,
                              APITestCase):
    viewclass = groupcomment_examiner.GroupCommentViewExaminer

    def test_filter_id(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   id=63,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id, queryparams='?id=63')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 63)

    def test_filter_id_not_found(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        mommy.make('devilry_group.GroupComment',
                   id=60,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id, queryparams='?id=63')
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_ordering_id_asc(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        for i in range(1, 4):
            mommy.make('devilry_group.GroupComment',
                       id=i,
                       visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                       user=examiner.relatedexaminer.user,
                       feedback_set=feedbackset,
                       user_role=GroupComment.USER_ROLE_EXAMINER,
                       comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id, queryparams='?ordering=id')
        self.assertEqual(200, response.status_code)
        self.assertEqual([comment['id'] for comment in response.data], [1, 2, 3])

    def test_ordering_id_desc(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        for i in range(1, 4):
            mommy.make('devilry_group.GroupComment',
                       id=i,
                       visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                       user=examiner.relatedexaminer.user,
                       feedback_set=feedbackset,
                       user_role=GroupComment.USER_ROLE_EXAMINER,
                       comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id, queryparams='?ordering=-id')
        self.assertEqual(200, response.status_code)
        self.assertEqual([comment['id'] for comment in response.data], [3, 2, 1])
