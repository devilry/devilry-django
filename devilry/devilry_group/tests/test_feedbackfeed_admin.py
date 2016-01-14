from django.test import TestCase
from devilry.devilry_group.tests import test_feedbackfeed_common
from devilry.devilry_group.views import feedbackfeed_admin


class TestFeedbackfeedAdmin(TestCase, test_feedbackfeed_common.TestFeedbackFeedMixin):
    viewclass = feedbackfeed_admin.AdminFeedbackFeedView

    def test_get(self):
        pass
