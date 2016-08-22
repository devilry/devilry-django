# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.devilry_api import devilry_api_mommy_factories as api_mommy
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_api.tests.mixins import test_student_mixins, api_test_helper, test_common_mixins
from devilry.devilry_api.group_comment.views import groupcomment_student
from devilry.devilry_group.models import GroupComment
from devilry.apps.core.models import Assignment


class TestGroupCommentSanity(test_common_mixins.TestReadOnlyPermissionMixin,
                             test_student_mixins.TestAuthAPIKeyStudentMixin,
                             api_test_helper.TestCaseMixin,
                             APITestCase):
    viewclass = groupcomment_student.GroupCommentViewStudent

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_sanity(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = core_mommy.candidate(feedbackset.group)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 1)

    def test_published_datetime(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = core_mommy.candidate(feedbackset.group)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        comment = mommy.make('devilry_group.GroupComment',
                             visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                             user=candidate.relatedstudent.user,
                             feedback_set=feedbackset,
                             user_role=GroupComment.USER_ROLE_STUDENT,
                             comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['published_datetime'], comment.published_datetime)

    def test_text(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = core_mommy.candidate(feedbackset.group)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   text='lol')
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['text'], 'lol')

    def test_id(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = core_mommy.candidate(feedbackset.group)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   id=20)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 20)

    def test_visibility(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = core_mommy.candidate(feedbackset.group)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['visibility'], GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

    def test_part_of_grading(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = core_mommy.candidate(feedbackset.group)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertFalse(response.data[0]['part_of_grading'])

    def test_user_fullname(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = core_mommy.candidate(feedbackset.group, fullname='Alice')
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['user_fullname'], 'Alice')

    def test_user_shortname(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = core_mommy.candidate(feedbackset.group, shortname='Alice@example.com')
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['user_shortname'], candidate.relatedstudent.user.shortname)

    def test_user_role(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = core_mommy.candidate(feedbackset.group)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['user_role'], GroupComment.USER_ROLE_STUDENT)


class TestGroupCommentAnonymization(api_test_helper.TestCaseMixin,
                                    APITestCase):
    viewclass = groupcomment_student.GroupCommentViewStudent

    def test_anonymization_off_examiner_user_fullname(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        examiner = core_mommy.examiner(group=feedbackset.group, fullname='Thor')
        candidate = core_mommy.candidate(group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(response.data[0]['user_fullname'], 'Thor')

    def test_anonymization_semi_examiner_user_fullname(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = core_mommy.examiner(group=feedbackset.group, fullname='Thor',
                                       automatic_anonymous_id='lol')
        candidate = core_mommy.candidate(group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(response.data[0]['user_fullname'], 'lol')

    def test_anonymization_full_examiner_user_fullname(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        examiner = core_mommy.examiner(group=feedbackset.group, fullname='Thor')
        candidate = core_mommy.candidate(group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        print(response.data[0]['user_fullname'])
        self.assertEqual(response.data[0]['user_fullname'], 'Anonymous ID missing')

    def test_anonymization_off_examiner_user_shortname(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        examiner = core_mommy.examiner(group=feedbackset.group, shortname='Thor@example.com')
        candidate = core_mommy.candidate(group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(response.data[0]['user_shortname'], 'Thor@example.com')

    def test_anonymization_semi_examiner_user_shortname(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = core_mommy.examiner(group=feedbackset.group, shortname='Thor@example.com',
                                       automatic_anonymous_id='lol')
        candidate = core_mommy.candidate(group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(response.data[0]['user_shortname'], 'lol')

    def test_anonymization_full_examiner_user_shortname(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        examiner = core_mommy.examiner(group=feedbackset.group, shortname='Thor@example.com')
        candidate = core_mommy.candidate(group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(response.data[0]['user_shortname'], 'Anonymous ID missing')

    def test_anonymization_off_student_user_fullname(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        candidate1 = core_mommy.candidate(group=feedbackset.group, fullname='Alice')
        candidate = core_mommy.candidate(group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate1.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(response.data[0]['user_fullname'], 'Alice')

    def test_anonymization_semi_student_user_fullname(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate1 = core_mommy.candidate(group=feedbackset.group, fullname='Alice',
                                          automatic_anonymous_id='lol')
        candidate = core_mommy.candidate(group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate1.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(response.data[0]['user_fullname'], 'Alice')

    def test_anonymization_full_student_user_fullname(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        candidate1 = core_mommy.candidate(group=feedbackset.group, fullname='Alice')
        candidate = core_mommy.candidate(group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate1.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        print(response.data[0]['user_fullname'])
        self.assertEqual(response.data[0]['user_fullname'], 'Alice')

    def test_anonymization_off_student_user_shortname(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        candidate1 = core_mommy.candidate(group=feedbackset.group, shortname='Alice@example.com')
        candidate = core_mommy.candidate(group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate1.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(response.data[0]['user_shortname'], 'Alice@example.com')

    def test_anonymization_semi_student_user_shortname(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate1 = core_mommy.candidate(group=feedbackset.group, shortname='Alice@example.com',
                                          automatic_anonymous_id='lol')
        candidate = core_mommy.candidate(group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate1.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(response.data[0]['user_shortname'], 'Alice@example.com')

    def test_anonymization_full_student_user_shortname(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        candidate1 = core_mommy.candidate(group=feedbackset.group, shortname='Alice@example.com')
        candidate = core_mommy.candidate(group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=candidate1.relatedstudent.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(response.data[0]['user_shortname'], 'Alice@example.com')


class TestGroupCommentVisibility(api_test_helper.TestCaseMixin,
                                 APITestCase):
    viewclass = groupcomment_student.GroupCommentViewStudent

    def test_visible_to_everyone(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        examiner = core_mommy.examiner(feedbackset.group)
        candidate = core_mommy.candidate(feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   id=10,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 10)

    def test_visible_private(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        examiner = core_mommy.examiner(feedbackset.group)
        candidate = core_mommy.candidate(feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_PRIVATE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_visible_to_examiner_and_admins(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        examiner = core_mommy.examiner(feedbackset.group)
        candidate = core_mommy.candidate(feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)


class TestGroupCommentFilters(api_test_helper.TestCaseMixin,
                              APITestCase):
    viewclass = groupcomment_student.GroupCommentViewStudent

    def test_filter_id(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        examiner = core_mommy.examiner(feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   id=63,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        candidate = core_mommy.candidate(feedbackset.group)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key, queryparams='?id=63')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 63)

    def test_filter_id_not_found(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        examiner = core_mommy.examiner(feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   id=60,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user=examiner.relatedexaminer.user,
                   feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        candidate = core_mommy.candidate(feedbackset.group)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key, queryparams='?id=63')
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_ordering_id_asc(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        examiner = core_mommy.examiner(feedbackset.group)
        for i in range(1, 4):
            mommy.make('devilry_group.GroupComment',
                       id=i,
                       visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                       user=examiner.relatedexaminer.user,
                       feedback_set=feedbackset,
                       user_role=GroupComment.USER_ROLE_EXAMINER,
                       comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
            examiner = core_mommy.examiner(feedbackset.group)
        candidate = core_mommy.candidate(feedbackset.group)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key, queryparams='?ordering=id')
        self.assertEqual(200, response.status_code)
        self.assertEqual([comment['id'] for comment in response.data], [1, 2, 3])

    def test_ordering_id_desc(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        examiner = core_mommy.examiner(feedbackset.group)
        for i in range(1, 4):
            mommy.make('devilry_group.GroupComment',
                       id=i,
                       visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                       user=examiner.relatedexaminer.user,
                       feedback_set=feedbackset,
                       user_role=GroupComment.USER_ROLE_EXAMINER,
                       comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        candidate = core_mommy.candidate(feedbackset.group)
        apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(feedback_set=feedbackset.id, apikey=apikey.key, queryparams='?ordering=-id')
        self.assertEqual(200, response.status_code)
        self.assertEqual([comment['id'] for comment in response.data], [3, 2, 1])


class TestPostComment(api_test_helper.TestCaseMixin,
                      APITestCase):
    viewclass = groupcomment_student.GroupCommentViewStudent

    def test_unauthorized_401(self):
        response = self.mock_post_request(feedbackset=1)
        self.assertEqual(401, response.status_code)

    def test_not_part_of_assignemnt_group(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(id=10)
        candidate = core_mommy.candidate(group=mommy.make('core.AssignmentGroup'))
        apikey = api_mommy.api_key_student_permission_write(user=candidate.relatedstudent.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={'text': 'hei'})
        self.assertEqual(400, response.status_code)
        self.assertEqual(['Access denied Student not part of assignment group'], response.data['feedback_set'])

    def test_post_comment_sanity(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(id=10)
        candidate = core_mommy.candidate(group=feedbackset.group)
        apikey = api_mommy.api_key_student_permission_write(user=candidate.relatedstudent.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={'text': 'hei'})
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['text'], 'hei')
        self.assertEqual(response.data['user_role'], 'student')
        self.assertEqual(response.data['visibility'], 'visible-to-everyone')
        self.assertEqual(response.data['feedback_set'], 10)
        self.assertEqual(response.data['part_of_grading'], False)

    def test_post_comment_no_text(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(id=10)
        candidate = core_mommy.candidate(group=feedbackset.group)
        apikey = api_mommy.api_key_student_permission_write(user=candidate.relatedstudent.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id)
        self.assertEqual(400, response.status_code)

    def test_post_user_role_cannot_be_examiner(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(id=10)
        candidate = core_mommy.candidate(group=feedbackset.group)
        apikey = api_mommy.api_key_student_permission_write(user=candidate.relatedstudent.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={
            'text': 'hei',
            'user_role': 'examiner'
        })
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['user_role'], 'student')

    def test_post_user_role_cannot_be_admin(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(id=10)
        candidate = core_mommy.candidate(group=feedbackset.group)
        apikey = api_mommy.api_key_student_permission_write(user=candidate.relatedstudent.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={
            'text': 'hei',
            'user_role': 'admin'
        })
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['user_role'], 'student')

    def test_post_visibility_cannot_be_private(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(id=10)
        candidate = core_mommy.candidate(group=feedbackset.group)
        apikey = api_mommy.api_key_student_permission_write(user=candidate.relatedstudent.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={
            'text': 'hei',
            'visibility': 'private'
        })
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['visibility'], 'visible-to-everyone')

    def test_post_visibility_cannot_be_visible_to_examiner_and_admin(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(id=10)
        candidate = core_mommy.candidate(group=feedbackset.group)
        apikey = api_mommy.api_key_student_permission_write(user=candidate.relatedstudent.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={
            'text': 'hei',
            'visibility': 'visible-to-examiner-and-admins'
        })
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['visibility'], 'visible-to-everyone')

    def test_post_part_of_grading_cannot_be_true(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(id=10)
        candidate = core_mommy.candidate(group=feedbackset.group)
        apikey = api_mommy.api_key_student_permission_write(user=candidate.relatedstudent.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={
            'text': 'hei',
            'part_of_grading': True
        })
        self.assertEqual(201, response.status_code)
        self.assertFalse(response.data['part_of_grading'])

    def test_post_is_added_to_db(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(id=10)
        candidate = core_mommy.candidate(group=feedbackset.group)
        apikey = api_mommy.api_key_student_permission_write(user=candidate.relatedstudent.user)
        response = self.mock_post_request(apikey=apikey.key, feedback_set=feedbackset.id, data={'text': 'hei'})
        self.assertEqual(201, response.status_code)
        comment = GroupComment.objects.get(id=response.data['id'])
        self.assertEqual(response.data['id'], comment.id)
        self.assertEqual(response.data['feedback_set'], comment.feedback_set.id)
        self.assertEqual(response.data['published_datetime'], comment.published_datetime)
        self.assertEqual(response.data['text'], comment.text)
        self.assertEqual(response.data['visibility'], comment.visibility)
        self.assertEqual(response.data['part_of_grading'], comment.part_of_grading)
        self.assertEqual(response.data['user_role'], comment.user_role)
