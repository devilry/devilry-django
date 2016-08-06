# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf import settings
from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.apps.core import devilry_core_mommy_factories
from devilry.devilry_api import devilry_api_mommy_factories
from devilry.devilry_api.feedbackset.views import feedbackset_student
from devilry.devilry_api.tests.mixins import test_examiner_mixins, api_test_helper, test_common_mixins


class TestFeedbacksetSanity(test_common_mixins.TestReadOnlyPermissionMixin,
                            test_examiner_mixins.TestAuthAPIKeyExaminerMixin,
                            api_test_helper.TestCaseMixin,
                            APITestCase):
    viewclass = feedbackset_student.FeedbacksetListViewStudent

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_sanity(self):
        set = mommy.make('devilry_group.Feedbackset')
        examiner = devilry_core_mommy_factories.examiner(set.group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
