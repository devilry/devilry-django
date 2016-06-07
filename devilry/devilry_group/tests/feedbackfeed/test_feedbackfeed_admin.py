from django.test import TestCase
from model_mommy import mommy

from devilry.devilry_group.tests.feedbackfeed.mixins import test_feedbackfeed_common
from devilry.devilry_group.views import feedbackfeed_admin
from devilry.devilry_group import models


class TestFeedbackfeedAdmin(TestCase, test_feedbackfeed_common.TestFeedbackFeedMixin):
    viewclass = feedbackfeed_admin.AdminFeedbackFeedView

    def test_get(self):
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized,
                          candidate.assignment_group.assignment.get_path())

    def test_get_feedbackfeed_comment_admin(self):
        admin = mommy.make('devilry_account.User', shortname='periodadmin', fullname='Thor the norse god')
        period = mommy.make_recipe('devilry.apps.core.period_active',
                                   admins=[admin],
                                   parentnode__admins=[mommy.make('devilry_account.User', shortname='subjectadmin')],
                                   parentnode__parentnode__admins=[mommy.make('devilry_account.User',
                                                                              shortname='nodeadmin')])

        comment = mommy.make('devilry_group.GroupComment',
                             user_role='admin',
                             user=admin,
                             text='Hello, is it me you\'re looking for?',
                             feedback_set__group__parentnode__parentnode=period,
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-admin'))

    def test_get_feedbackfeed_admin_wysiwyg_get_comment_choise_add_comment_for_examiners_and_admins_button(self):
        # examiner = mommy.make('core.Examiner')
        group = mommy.make('devilry_group.FeedbackSet')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group.group)
        self.assertTrue(mockresponse.selector.exists('#submit-id-administrator_add_comment_for_examiners'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_public_button(self):
        examiner = mommy.make('core.Examiner')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-administrator_add_public_comment'))
