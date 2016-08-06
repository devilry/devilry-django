# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf import settings
from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.apps.core import devilry_core_mommy_factories
from devilry.devilry_api import devilry_api_mommy_factories
from devilry.devilry_api.feedbackset.views import feedbackset_student
from devilry.devilry_api.tests.mixins import test_student_mixins, api_test_helper, test_common_mixins


class TestFeedbacksetSanity(test_common_mixins.TestReadOnlyPermissionMixin,
                            test_student_mixins.TestAuthAPIKeyStudentMixin,
                            api_test_helper.TestCaseMixin,
                            APITestCase):
    viewclass = feedbackset_student.FeedbacksetListViewStudent

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_sanity(self):
        set = mommy.make('devilry_group.Feedbackset')
        candidate = devilry_core_mommy_factories.candidate(set.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)

    def test_id(self):
        set = mommy.make('devilry_group.Feedbackset', id=10)
        candidate = devilry_core_mommy_factories.candidate(set.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 10)

    def test_group(self):
        set = mommy.make('devilry_group.Feedbackset',
                         group=mommy.make('core.AssignmentGroup', id=10))
        candidate = devilry_core_mommy_factories.candidate(set.group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['group'], 10)

    