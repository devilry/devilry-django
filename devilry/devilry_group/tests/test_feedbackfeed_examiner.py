from django.utils import timezone
from django.test import TestCase, RequestFactory
import htmls
import mock
from model_mommy import mommy

from devilry.devilry_group.tests import test_feedbackfeed_common
from devilry.devilry_group.views import feedbackfeed_examiner
from devilry.project.develop.testhelpers.corebuilder import UserBuilder2, AssignmentGroupBuilder, FeedbackSetBuilder


class TestFeedbackfeedExaminer(TestCase, test_feedbackfeed_common.TestFeedbackFeedMixin):
    viewclass = feedbackfeed_examiner.ExaminerFeedbackFeedView

    def test_get(self):
        examiner = mommy.make('core.Examiner')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.user)
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized,
                          examiner.assignmentgroup.assignment.get_path())

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_for_examiners(self):
        examiner = mommy.make('core.Examiner')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group,
                                                          requestuser=examiner.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_add_comment_for_examiners'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_public(self):
        examiner = mommy.make('core.Examiner')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group,
                                                          requestuser=examiner.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_add_public_comment'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_to_feedbackdraft(self):
        examiner = mommy.make('core.Examiner')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group,
                                                          requestuser=examiner.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_add_comment_to_feedback_draft'))
