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
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        group_builder = AssignmentGroupBuilder.make()
        selector, request = self._mock_http200_getrequest_htmls(role=group_builder.get_object(),
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertEqual(selector.one('title').alltext_normalized,
                         group_builder.group.assignment.get_path())

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_for_examiners(self):
        janedoe = UserBuilder2(fullname='Jane Doe').user
        time = timezone.now()
        feedbackset_builder = FeedbackSetBuilder.make(
            group__assignment__first_deadline=time,
            deadline_datetime = time
        )
        selector, request = self._mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=janedoe,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('#submit-id-examiner_add_comment_for_examiners'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_public(self):
        janedoe = UserBuilder2(fullname='Jane Doe').user
        time = timezone.now()
        feedbackset_builder = FeedbackSetBuilder.make(
            group__assignment__first_deadline=time,
            deadline_datetime = time
        )
        selector, request = self._mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=janedoe,
                                                                 group=janedoe)
        self.assertTrue(selector.one('#submit-id-examiner_add_public_comment'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_to_feedbackdraft(self):
        janedoe = UserBuilder2(fullname='Jane Doe').user
        time = timezone.now()
        feedbackset_builder = FeedbackSetBuilder.make(
            group__assignment__first_deadline=time,
            deadline_datetime = time
        )
        selector, request = self._mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=janedoe,
                                                                 group=janedoe)
        self.assertTrue(selector.one('#submit-id-examiner_add_comment_to_feedback_draft'))


    def test_post(self):
        janedoe = UserBuilder2(fullname='Jane Doe').user
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        assignment_group = mommy.make('core.AssignmentGroup')
        response, request = self._mock_postrequest(role=assignment_group, requestuser=janedoe, group=janedoe)

        self.assertEquals(response.status_code, 200)
