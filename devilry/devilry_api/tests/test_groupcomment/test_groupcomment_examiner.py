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


class TestGroupCommentPost(api_test_helper.TestCaseMixin,
                           APITestCase):
    viewclass = groupcomment_examiner.GroupCommentViewExaminer

    def test_unauthorized_401(self):
        response = self.mock_post_request(feedbackset=1)
        self.assertEqual(401, response.status_code)

    def test_not_part_of_assignment_group(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=mommy.make('core.AssignmentGroup'))
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={'text': 'hei'})
        self.assertEqual(400, response.status_code)
        self.assertEqual(['Access denied Examiner not part of assignment group'], response.data['feedback_set'])

    def test_part_of_assignment_group_old_period(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_oldperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={'text': 'hei'})
        self.assertEqual(400, response.status_code)
        self.assertEqual(['Access denied Examiner not part of assignment group'], response.data['feedback_set'])

    def test_post_comment_sanity(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group, id=10)
        examiner = core_mommy.examiner(group=group)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={'text': 'hei'})
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['text'], 'hei')
        self.assertEqual(response.data['user_role'], 'examiner')
        self.assertEqual(response.data['visibility'], 'visible-to-everyone')
        self.assertEqual(response.data['feedback_set'], 10)
        self.assertEqual(response.data['part_of_grading'], False)

    def test_post_comment_no_text(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(400, response.status_code)

    def test_post_user_role_cannot_be_student(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={
            'text': 'hei',
            'user_role': 'student'
        })
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['user_role'], 'examiner')

    def test_post_user_role_cannot_be_admin(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={
            'text': 'hei',
            'user_role': 'admin'
        })
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['user_role'], 'examiner')

    def test_post_visibility_private_part_of_grading_false(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={
            'text': 'hei',
            'visibility': GroupComment.VISIBILITY_PRIVATE,
            'part_of_grading': False
        })
        self.assertEqual(400, response.status_code)
        self.assertEqual(['if visibility = private, part_of_grading has to be True'], response.data['visibility'])

    def test_post_visibility_everyone_part_of_grading_true(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={
            'text': 'hei',
            'visibility': GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
            'part_of_grading': True
        })
        self.assertEqual(400, response.status_code)
        self.assertEqual(['if part_of_grading = True, visibility has to be private'], response.data['part_of_grading'])

    def test_post_part_of_grading_True_published_feedbackset(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_published(group=group, id=10)
        examiner = core_mommy.examiner(group=group)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={
            'text': 'hei',
            'visibility': GroupComment.VISIBILITY_PRIVATE,
            'part_of_grading': True
        })
        self.assertEqual(400, response.status_code)
        self.assertEqual(['Cannot post part of grading comment when grading is published'],
                         response.data['part_of_grading'])

    def test_post_part_of_grading_True_visibility_private_success(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group, id=10)
        examiner = core_mommy.examiner(group=group)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={
            'text': 'hei',
            'visibility': GroupComment.VISIBILITY_PRIVATE,
            'part_of_grading': True
        })
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['text'], 'hei')
        self.assertEqual(response.data['feedback_set'], 10)
        self.assertEqual(response.data['visibility'], GroupComment.VISIBILITY_PRIVATE)
        self.assertTrue(response.data['part_of_grading'])
        self.assertEqual(response.data['user_role'], GroupComment.USER_ROLE_EXAMINER)

    def test_post_visible_to_examiner_and_admins(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group, id=10)
        examiner = core_mommy.examiner(group=group)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={
            'text': 'hei',
            'visibility': GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS
        })
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['text'], 'hei')
        self.assertEqual(response.data['feedback_set'], 10)
        self.assertEqual(response.data['visibility'], GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        self.assertFalse(response.data['part_of_grading'])
        self.assertEqual(response.data['user_role'], GroupComment.USER_ROLE_EXAMINER)


class TestGroupCommentDeleteDraft(api_test_helper.TestCaseMixin,
                                  APITestCase):
    viewclass = groupcomment_examiner.GroupCommentViewExaminer

    def test_unauthorized_401(self):
        response = self.mock_delete_request(feedback_set=10, data={'id': 5})
        self.assertEqual(401, response.status_code)

    def test_delete_comment_404(self):
        examiner = core_mommy.examiner(group=mommy.make('core.AssignmentGroup'))
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_delete_request(apikey=apikey.key, feedback_set=10, queryparams='?id=5')
        self.assertEqual(404, response.status_code)

    def test_queryparam_id_required(self):
        examiner = core_mommy.examiner(group=mommy.make('core.AssignmentGroup'))
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_delete_request(apikey=apikey.key, feedback_set=10)
        self.assertEqual(400, response.status_code)
        self.assertEqual(response.data, ['Queryparam id required.'])

    def test_url_path_paramter_required(self):
        examiner = core_mommy.examiner(group=mommy.make('core.AssignmentGroup'))
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_delete_request(apikey=apikey.key)
        self.assertEqual(400, response.status_code)
        self.assertEqual(response.data, ['Url path parameter feedback_set required'])

    def test_cannot_delete_published_comment(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_published(group=group)
        examiner = core_mommy.examiner(group=group)
        comment = mommy.make('devilry_group.GroupComment',
                             visibility=GroupComment.VISIBILITY_PRIVATE,
                             user=examiner.relatedexaminer.user,
                             feedback_set=feedbackset,
                             user_role=GroupComment.USER_ROLE_EXAMINER,
                             comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                             part_of_grading=True)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_delete_request(apikey=apikey.key,
                                            feedback_set=feedbackset.id,
                                            queryparams='?id={}'.format(comment.id))
        self.assertEqual(403, response.status_code)
        self.assertEqual('Cannot delete published comment.', response.data['detail'])

    def test_cannot_delete_comment_visible_everyone(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        comment = mommy.make('devilry_group.GroupComment',
                             visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                             user=examiner.relatedexaminer.user,
                             feedback_set=feedbackset,
                             user_role=GroupComment.USER_ROLE_EXAMINER,
                             comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_delete_request(apikey=apikey.key,
                                            feedback_set=feedbackset.id,
                                            queryparams='?id={}'.format(comment.id))
        self.assertEqual(403, response.status_code)
        self.assertEqual('Cannot delete a comment that is not private.', response.data['detail'])

    def test_cannot_delete_comment_visible_examiner_and_admins(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        comment = mommy.make('devilry_group.GroupComment',
                             visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                             user=examiner.relatedexaminer.user,
                             feedback_set=feedbackset,
                             user_role=GroupComment.USER_ROLE_EXAMINER,
                             comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_delete_request(apikey=apikey.key,
                                            feedback_set=feedbackset.id,
                                            queryparams='?id={}'.format(comment.id))
        self.assertEqual(403, response.status_code)
        self.assertEqual('Cannot delete a comment that is not private.', response.data['detail'])

    def test_cannot_delete_comment_part_of_grading_false(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        comment = mommy.make('devilry_group.GroupComment',
                             visibility=GroupComment.VISIBILITY_PRIVATE,
                             user=examiner.relatedexaminer.user,
                             feedback_set=feedbackset,
                             user_role=GroupComment.USER_ROLE_EXAMINER,
                             comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                             part_of_grading=False)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_delete_request(apikey=apikey.key,
                                            feedback_set=feedbackset.id,
                                            queryparams='?id={}'.format(comment.id))
        self.assertEqual(403, response.status_code)
        self.assertEqual('Cannot delete a comment that is not a draft.', response.data['detail'])

    def test_delete_another_examiners_draft_same_group(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        requset_examiner = core_mommy.examiner(group=group)
        examiner = core_mommy.examiner(group=group)
        comment = mommy.make('devilry_group.GroupComment',
                             visibility=GroupComment.VISIBILITY_PRIVATE,
                             user=examiner.relatedexaminer.user,
                             feedback_set=feedbackset,
                             user_role=GroupComment.USER_ROLE_EXAMINER,
                             comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                             part_of_grading=True)
        apikey = api_mommy.api_key_examiner_permission_write(user=requset_examiner.relatedexaminer.user)
        response = self.mock_delete_request(apikey=apikey.key,
                                            feedback_set=feedbackset.id,
                                            queryparams='?id={}'.format(comment.id))
        self.assertEqual(404, response.status_code)

    def test_delete_draft_not_part_of_assignment_group(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        requset_examiner = core_mommy.examiner(group=mommy.make('core.AssignmentGroup'))
        examiner = core_mommy.examiner(group=group)
        comment = mommy.make('devilry_group.GroupComment',
                             visibility=GroupComment.VISIBILITY_PRIVATE,
                             user=examiner.relatedexaminer.user,
                             feedback_set=feedbackset,
                             user_role=GroupComment.USER_ROLE_EXAMINER,
                             comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                             part_of_grading=True)
        apikey = api_mommy.api_key_examiner_permission_write(user=requset_examiner.relatedexaminer.user)
        response = self.mock_delete_request(apikey=apikey.key,
                                            feedback_set=feedbackset.id,
                                            queryparams='?id={}'.format(comment.id))
        self.assertEqual(404, response.status_code)

    def test_delete_draft_from_old_period_assignment_group(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_oldperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        comment = mommy.make('devilry_group.GroupComment',
                             visibility=GroupComment.VISIBILITY_PRIVATE,
                             user=examiner.relatedexaminer.user,
                             feedback_set=feedbackset,
                             user_role=GroupComment.USER_ROLE_EXAMINER,
                             comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                             part_of_grading=True)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_delete_request(apikey=apikey.key,
                                            feedback_set=feedbackset.id,
                                            queryparams='?id={}'.format(comment.id))
        self.assertEqual(404, response.status_code)

    def test_delete_sanity(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        comment = mommy.make('devilry_group.GroupComment',
                             visibility=GroupComment.VISIBILITY_PRIVATE,
                             user=examiner.relatedexaminer.user,
                             feedback_set=feedbackset,
                             user_role=GroupComment.USER_ROLE_EXAMINER,
                             comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                             part_of_grading=True)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_delete_request(apikey=apikey.key,
                                            feedback_set=feedbackset.id,
                                            queryparams='?id={}'.format(comment.id))
        self.assertEqual(204, response.status_code)

    def test_comment_is_deleted_from_db(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=group)
        examiner = core_mommy.examiner(group=group)
        comment = mommy.make('devilry_group.GroupComment',
                             id=55,
                             visibility=GroupComment.VISIBILITY_PRIVATE,
                             user=examiner.relatedexaminer.user,
                             feedback_set=feedbackset,
                             user_role=GroupComment.USER_ROLE_EXAMINER,
                             comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                             part_of_grading=True)
        apikey = api_mommy.api_key_examiner_permission_write(user=examiner.relatedexaminer.user)
        response = self.mock_delete_request(apikey=apikey.key,
                                            feedback_set=feedbackset.id,
                                            queryparams='?id={}'.format(comment.id))
        self.assertEqual(204, response.status_code)
        with self.assertRaises(GroupComment.DoesNotExist):
            GroupComment.objects.get(id=55)
