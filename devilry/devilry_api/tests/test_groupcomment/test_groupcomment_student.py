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
                   user_role=GroupComment.USER_ROLE_STUDENT)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 1)
