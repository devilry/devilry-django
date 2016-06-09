from django.test import TestCase
from django.utils import timezone
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

    def test_get_feedbackfeed_event_delivery_passed(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode__max_points=10,
                                 group__parentnode__passing_grade_min_points=5,
                                 grading_published_datetime=timezone.now(),
                                 deadline_datetime=timezone.now(),
                                 grading_points=7)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-core-grade-passed'))

    def test_get_feedbackfeed_event_delivery_failed(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode__max_points=10,
                                 group__parentnode__passing_grade_min_points=5,
                                 grading_published_datetime=timezone.now(),
                                 grading_points=3)

        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-core-grade-failed'))

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
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('#submit-id-administrator_add_comment_for_examiners'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_public_button(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('#submit-id-administrator_add_public_comment'))

    def test_post_feedbackset_comment_visible_to_everyone(self):
        admin = mommy.make('devilry_account.User', shortname='periodadmin', fullname='Thor')
        period = mommy.make_recipe('devilry.apps.core.period_active',
                                   admins=[admin])
        group = mommy.make('core.AssignmentGroup', parentnode__parentnode=period)
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=group)
        self.mock_http302_postrequest(
            cradmin_role=group,
            requestuser=admin,
            viewkwargs={'pk': group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment',
                    'admin_add_public_comment': 'unused value'
                }
            })
        comments = models.GroupComment.objects.all()
        self.assertEquals(1, len(comments))
        self.assertEquals('visible-to-everyone', comments[0].visibility)
        self.assertEquals('periodadmin', comments[0].user.shortname)
        self.assertEquals(feedbackset.id, comments[0].feedback_set.id)

    def test_post_feedbackset_comment_visible_to_examiner_and_admins(self):
        admin = mommy.make('devilry_account.User', shortname='periodadmin', fullname='Thor')
        period = mommy.make_recipe('devilry.apps.core.period_active',
                                   admins=[admin])
        group = mommy.make('core.AssignmentGroup', parentnode__parentnode=period)
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=group)
        self.mock_http302_postrequest(
            cradmin_role=group,
            requestuser=admin,
            viewkwargs={'pk': group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment',
                    'admin_add_comment_for_examiners': 'unused value'
                }
            })
        comments = models.GroupComment.objects.all()
        self.assertEquals(1, len(comments))
        self.assertEquals('visible-to-examiner-and-admins', comments[0].visibility)
        self.assertEquals('periodadmin', comments[0].user.shortname)
        self.assertEquals(feedbackset.id, comments[0].feedback_set.id)
