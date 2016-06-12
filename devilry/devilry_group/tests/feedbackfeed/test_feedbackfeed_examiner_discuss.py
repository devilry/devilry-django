from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_comment.models import Comment
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models as group_models
from devilry.devilry_group.tests.feedbackfeed.mixins import test_feedbackfeed_examiner
from devilry.devilry_group.views import feedbackfeed_examiner


class TestFeedbackfeedExaminerDiscuss(TestCase, test_feedbackfeed_examiner.TestFeedbackfeedExaminerMixin):
    viewclass = feedbackfeed_examiner.ExaminerDiscussView

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_for_examiners_and_admins_button(self):
        examiner = mommy.make('core.Examiner')
        mommy.make('devilry_group.FeedbackSet', group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_add_comment_for_examiners'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_public_button(self):
        examiner = mommy.make('core.Examiner')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_add_public_comment'))

    def test_get_no_form_grade_option(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=mommy.make('core.AssignmentGroup', parentnode=assignment),
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertFalse(mockresponse.selector.exists('#div_id_passed'))
        self.assertFalse(mockresponse.selector.exists('#div_id_points'))

    def test_get_examiner_no_comment_delete_option_when_published(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'),)
        feedbackset = group_mommy.feedbackset_first_attempt_published(group=examiner.assignmentgroup)
        comment = mommy.make('devilry_group.GroupComment',
                             user=examiner.relatedexaminer.user,
                             user_role='examiner',
                             part_of_grading=True,
                             text='this was a draft, and is now a feedback',
                             visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                             feedback_set=feedbackset)
        feedbackset.publish(published_by=examiner.relatedexaminer.user, grading_points=0)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)

        self.assertFalse(mockresponse.selector.exists('.btn-danger'))

    def test_post_feedbackset_comment_with_text(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', )
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment',
                }
            })
        self.assertEquals(1, len(group_models.GroupComment.objects.all()))

    def test_post_feedbackset_comment_with_text_published_datetime_is_set(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', )
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment',
                    'examiner_add_public_comment': 'unused value'
                }
            })
        self.assertIsNotNone(group_models.GroupComment.objects.all()[0].published_datetime)

    def test_post_feedbackset_comment_visible_to_everyone(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', )
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment',
                    'examiner_add_public_comment': 'unused value'
                }
            })
        self.assertEquals('visible-to-everyone', group_models.GroupComment.objects.all()[0].visibility)

    def test_post_feedbackset_comment_visible_to_examiner_and_admins(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', )
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment',
                    'examiner_add_comment_for_examiners': 'unused value'
                }
            })
        self.assertEquals('visible-to-examiner-and-admins', group_models.GroupComment.objects.all()[0].visibility)

    def test_post_comment_always_to_last_feedbackset(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)

        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))

        feedbackset_first = group_mommy.feedbackset_first_attempt_published(is_last_in_group=None, group=group)
        feedbackset_last = group_mommy.feedbackset_new_attempt_unpublished(group=group)
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a feedback',
                    'examiner_add_public_comment': 'unused value',
                }
            })
        comments = group_models.GroupComment.objects.all()
        self.assertEquals(len(comments), 1)
        self.assertNotEquals(feedbackset_first, comments[0].feedback_set)
        self.assertEquals(feedbackset_last, comments[0].feedback_set)

    def test_get_num_queries(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        feedbackset = mommy.make('devilry_group.FeedbackSet', is_last_in_group=False)
        feedbackset2 = mommy.make('devilry_group.FeedbackSet', group=feedbackset.group)

        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer__user=requestuser)

        mommy.make('devilry_group.GroupComment',
                   user=requestuser,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset,
                   _quantity=20)
        mommy.make('devilry_group.GroupComment',
                   user=requestuser,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset2,
                   _quantity=20)

        with self.assertNumQueries(7):
            mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                              requestuser=requestuser)
