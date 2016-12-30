from datetime import datetime

from django.test import TestCase
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import models as group_models
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group.tests.feedbackfeed.mixins import test_feedbackfeed_examiner
from devilry.devilry_group.views.examiner import feedbackfeed_examiner
from devilry.utils import datetimeutils


class TestFeedbackfeedExaminerFeedback(TestCase, test_feedbackfeed_examiner.TestFeedbackfeedExaminerMixin):
    """
    Tests the general function of the ExaminerFeedbackView.
    """
    viewclass = feedbackfeed_examiner.ExaminerFeedbackView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_no_redirect_on_last_feedbackset_unpublished(self):
        group = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_unpublished(group=examiner.assignmentgroup)
        mockresponse = self.mock_getrequest(cradmin_role=examiner.assignmentgroup,
                                            requestuser=examiner.relatedexaminer.user)
        self.assertEquals(mockresponse.response.status_code, 200)

    def test_redirect_on_last_feedbackset_published(self):
        group = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_published(group=examiner.assignmentgroup)
        mockresponse = self.mock_getrequest(cradmin_role=examiner.assignmentgroup,
                                            requestuser=examiner.relatedexaminer.user)
        self.assertEquals(mockresponse.response.status_code, 302)

    def test_get_feedbackset_first_no_created_deadline_event(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_get_feedbackset_second_created_deadline_event(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode=assignment,
            is_last_in_group=None)
        group_mommy.feedbackset_new_attempt_unpublished(group=feedbackset.group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_get_feedbackfeed_examiner_can_see_feedback_and_discuss_in_header(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-feedback-button'))
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-discuss-button'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_for_examiners_and_admins_button(self):
        examiner = mommy.make('core.Examiner')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_publish_feedback'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_to_feedbackdraft_button(self):
        examiner = mommy.make('core.Examiner')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_add_comment_to_feedback_draft'))

    def test_get_form_passedfailed_grade_option(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment
                                       .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=mommy.make('core.AssignmentGroup', parentnode=assignment),
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#div_id_passed'))
        self.assertFalse(mockresponse.selector.exists('#div_id_points'))

    def test_get_form_points_grade_option(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=mommy.make('core.AssignmentGroup', parentnode=assignment),
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertFalse(mockresponse.selector.exists('#div_id_passed'))
        self.assertTrue(mockresponse.selector.exists('#div_id_points'))

    def test_get_num_queries(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = mommy.make('devilry_group.FeedbackSet', group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=testfeedbackset)

        with self.assertNumQueries(10):
            self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                               requestuser=examiner.relatedexaminer.user)

    def test_get_num_queries_with_commentfiles(self):
        """
        NOTE: (works as it should)
        Checking that no more queries are executed even though the
        :func:`devilry.devilry_group.feedbackfeed_builder.FeedbackFeedTimelineBuilder.__get_feedbackset_queryset`
        duplicates comment_file query.
        """
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = mommy.make('devilry_group.FeedbackSet', group=testgroup)
        comment = mommy.make('devilry_group.GroupComment',
                             user=examiner.relatedexaminer.user,
                             user_role='examiner',
                             feedback_set=testfeedbackset)
        comment2 = mommy.make('devilry_group.GroupComment',
                              user=examiner.relatedexaminer.user,
                              user_role='examiner',
                              feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile',
                   filename='test.py',
                   comment=comment,
                   _quantity=100)
        mommy.make('devilry_comment.CommentFile',
                   filename='test2.py',
                   comment=comment2,
                   _quantity=100)
        with self.assertNumQueries(10):
            self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                               requestuser=examiner.relatedexaminer.user)

    # def test_feedbackfeed_view_publish_feedback(self):
    #     group = mommy.make('core.AssignmentGroup')
    #     examiner = mommy.make('core.Examiner',
    #                           assignmentgroup=group,
    #                           relatedexaminer=mommy.make('core.RelatedExaminer'))
    #     mommy.make('devilry_group.GroupComment',
    #                user=examiner.relatedexaminer.user,
    #                user_role='examiner',
    #                visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
    #                part_of_grading=True,
    #                published_datetime=timezone.now(),
    #                feedback_set__group=group)

    # def test_get_examiner_comment_part_of_grading_private(self):
    #     group = mommy.make('core.AssignmentGroup')
    #     examiner1 = mommy.make('core.Examiner',
    #                            assignmentgroup=group,
    #                            relatedexaminer=mommy.make('core.RelatedExaminer'),)
    #     examiner2 = mommy.make('core.Examiner',
    #                            assignmentgroup=group,
    #                            relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='Jane Doe'),)
    #     mommy.make('devilry_group.GroupComment',
    #                user=examiner2.relatedexaminer.user,
    #                user_role='examiner',
    #                part_of_grading=True,
    #                visibility=GroupComment.VISIBILITY_PRIVATE,
    #                published_datetime=timezone.now() - timezone.timedelta(days=1),
    #                feedback_set__group=group)
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner1.assignmentgroup,
    #                                                       requestuser=examiner1.relatedexaminer)
    #     self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))

    def test_post_feedbackdraft_comment_with_text(self):
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
                    'examiner_add_comment_to_feedback_draft': 'unused value'
                }
            })
        self.assertEquals(1, len(group_models.GroupComment.objects.all()))

    def test_post_feedbackset_comment_visibility_private(self):
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
                    'examiner_add_comment_to_feedback_draft': 'unused value'
                }
            })
        self.assertEquals('private', group_models.GroupComment.objects.all()[0].visibility)


class TestFeedbackFeedExaminerPublishFeedback(TestCase, test_feedbackfeed_examiner.TestFeedbackfeedExaminerMixin):
    """
    Explicitly tests creating drafts and publishing of the FeedbackSet.
    """
    viewclass = feedbackfeed_examiner.ExaminerFeedbackView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_post_can_not_publish_with_first_deadline_as_none(self):
        assignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED,
                first_deadline=None)
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        #self.assertEquals(2, group_models.FeedbackSet.objects.all().count())
        self.assertIsNone(group_models.FeedbackSet.objects.all()[0].grading_published_datetime)

    def test_post_can_not_publish_with_last_feedbackset_deadline_as_none(self):
        assignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_published(group=group, is_last_in_group=None)
        group_mommy.feedbackset_new_attempt_unpublished(group=group, deadline_datetime=None)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all().order_by('created_datetime')
        self.assertEquals(3, len(feedbacksets))
        self.assertIsNone(feedbacksets[0].grading_published_datetime)
        self.assertIsNotNone(feedbacksets[1].grading_published_datetime)
        self.assertIsNone(feedbacksets[2].grading_published_datetime)

    def test_post_publish_feedbackset_before_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_middle')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        self.assertIsNone(group_models.FeedbackSet.objects.all()[0].grading_published_datetime)

    def test_post_publish_feedbackset_after_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertIsNotNone(feedbacksets[1].grading_published_datetime)

    def test_post_publish_feedbackset_after_deadline_grading_system_points(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'points': 10,
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertIsNotNone(feedbacksets[1].grading_published_datetime)
        self.assertEquals(10, feedbacksets[1].grading_points)

    def test_post_publish_feedbackset_after_deadline_grading_system_passed_failed(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment
                                       .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertIsNotNone(feedbacksets[1].grading_published_datetime)
        self.assertEquals(1, feedbacksets[1].grading_points)

    def test_post_publish_feedbackset_drafts_on_last_feedbackset_only(self):
        assignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset_first = group_mommy.feedbackset_first_attempt_published(is_last_in_group=None, group=group)
        feedbackset_last = group_mommy.feedbackset_new_attempt_unpublished(group=group,
                                                                           deadline_datetime=timezone.now())
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        student = mommy.make('core.Candidate',
                             assignment_group=group,
                             relatedstudent=mommy.make('core.RelatedStudent'))
        mommy.make('devilry_group.GroupComment',
                   text='test text 1',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   feedback_set=feedbackset_first)
        comment2 = mommy.make('devilry_group.GroupComment',
                              text='test text 2',
                              user=examiner.relatedexaminer.user,
                              user_role='examiner',
                              part_of_grading=True,
                              feedback_set=feedbackset_last)
        self.mock_http302_postrequest(
            cradmin_role=student.assignment_group,
            requestuser=student.relatedstudent.user,
            viewkwargs={'pk': group.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': 'post comment',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        feedback_comments = group_models.GroupComment.objects.all().filter(feedback_set=feedbacksets[2])

        self.assertEquals(2, len(feedback_comments))
        self.assertEquals(feedback_comments[0], comment2)
        self.assertEquals(feedback_comments[1].text, 'post comment')

    def test_post_publish_feedbackset_after_deadline_test_publish_drafts_part_of_grading(self):
        assignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mommy.make('devilry_group.GroupComment',
                   text='test text 1',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   feedback_set=feedbackset)
        mommy.make('devilry_group.GroupComment',
                   text='test text 2',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   feedback_set=feedbackset)
        mommy.make('devilry_group.GroupComment',
                   text='test text 3',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   feedback_set=feedbackset)
        mommy.make('devilry_group.GroupComment',
                   text='test text 4',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   feedback_set=feedbackset)
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        feedback_comments = group_models.GroupComment.objects.all()
        self.assertIsNotNone(feedbacksets[1].grading_published_datetime)
        self.assertEquals(1, feedbacksets[1].grading_points)
        self.assertEquals(5, len(feedback_comments))

    def test_get_num_queries(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = mommy.make('devilry_group.FeedbackSet', group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=testfeedbackset)

        with self.assertNumQueries(10):
            self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                               requestuser=examiner.relatedexaminer.user)

    def test_get_num_queries_with_commentfiles(self):
        """
        NOTE: (works as it should)
        Checking that no more queries are executed even though the
        :func:`devilry.devilry_group.feedbackfeed_builder.FeedbackFeedTimelineBuilder.__get_feedbackset_queryset`
        duplicates comment_file query.
        """
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = mommy.make('devilry_group.FeedbackSet', group=testgroup)
        comment = mommy.make('devilry_group.GroupComment',
                             user=examiner.relatedexaminer.user,
                             user_role='examiner',
                             feedback_set=testfeedbackset)
        comment2 = mommy.make('devilry_group.GroupComment',
                              user=examiner.relatedexaminer.user,
                              user_role='examiner',
                              feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile',
                   filename='test.py',
                   comment=comment,
                   _quantity=100)
        mommy.make('devilry_comment.CommentFile',
                   filename='test2.py',
                   comment=comment2,
                   _quantity=100)
        with self.assertNumQueries(10):
            self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                               requestuser=examiner.relatedexaminer.user)

    # def test_examiner_publishes_without_comment_text(self):
    #     assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
    #                                    grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
    #     feedbackset = mommy.make('devilry_group.FeedbackSet',
    #                              group__parentnode=assignment)
    #     examiner = mommy.make('core.Examiner',
    #                           assignmentgroup=feedbackset.group,
    #                           relatedexaminer=mommy.make('core.RelatedExaminer'))
    #     self.mock_http302_postrequest(
    #         cradmin_role=examiner.assignmentgroup,
    #         requestuser=examiner.relatedexaminer.user,
    #         viewkwargs={'pk': feedbackset.group.id},
    #         requestkwargs={
    #             'data': {
    #                 'passed': True,
    #                 'text': '',
    #                 'examiner_publish_feedback': 'unused value',
    #             }
    #         })
    #     feedbacksets = group_models.FeedbackSet.objects.all()
    #     self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
    #     self.assertEquals(0, group_models.GroupComment.objects.all().count())
    #
    # def test_examiner_publishes_with_comment_text(self):
    #     assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
    #                                    grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
    #     feedbackset = mommy.make('devilry_group.FeedbackSet',
    #                              group__parentnode=assignment)
    #     examiner = mommy.make('core.Examiner',
    #                           assignmentgroup=feedbackset.group,
    #                           relatedexaminer=mommy.make('core.RelatedExaminer'))
    #     self.mock_http302_postrequest(
    #         cradmin_role=examiner.assignmentgroup,
    #         requestuser=examiner.relatedexaminer.user,
    #         viewkwargs={'pk': feedbackset.group.id},
    #         requestkwargs={
    #             'data': {
    #                 'passed': True,
    #                 'text': 'test',
    #                 'examiner_publish_feedback': 'unused value',
    #             }
    #         })
    #     feedbacksets = group_models.FeedbackSet.objects.all()
    #     self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
    #     self.assertEquals(1, group_models.GroupComment.objects.all().count())

    # def test_post_comment_file(self):
    #     feedbackset = mommy.make('devilry_group.FeedbackSet')
    #     filecollection = mommy.make(
    #         'cradmin_temporaryfileuploadstore.TemporaryFileCollection',
    #     )
    #     test_file = mommy.make(
    #         'cradmin_temporaryfileuploadstore.TemporaryFile',
    #         filename='test.txt',
    #         collection=filecollection
    #     )
    #     test_file.file.save('test.txt', ContentFile('test'))
    #     self.mock_http302_postrequest(
    #         cradmin_role=feedbackset.group,
    #         viewkwargs={'pk': feedbackset.group.id},
    #         requestkwargs={
    #             'data': {
    #                 'text': 'This is a comment',
    #                 'temporary_file_collection_id': filecollection.id,
    #             }
    #         })
    #     comment_files = comment_models.CommentFile.objects.all()
    #     self.assertEquals(1, len(comment_files))


class TestExaminerCreateNewFeedbackSet(TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    Only tests the layout of the view when redirected there. Does not test whether or not this is the right
    view to be in - that is handled by the ExaminerFeedbackView and is tested in
    TestFeedbackfeedExaminerFeedback.
    """
    viewclass = feedbackfeed_examiner.ExaminerFeedbackCreateFeedbackSetView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_feedbackset_first_no_created_deadline_event(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_published(group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_examiner_can_see_deadline_picker(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_published(group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('#id_deadline_datetime_triggerbutton'))

    def test_examiner_can_only_see_new_feedbackset_button(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_published(group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_create_new_feedbackset'))

    def test_examiner_can_not_see_publish_and_draft_buttons(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_published(group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertFalse(mockresponse.selector.exists('#submit-id-examiner_publish_feedback'))
        self.assertFalse(mockresponse.selector.exists('#submit-id-examiner_add_comment_to_feedback_draft'))

    def test_get_feedbackset_second_created_deadline_event(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_published(
            group__parentnode=assignment,
            is_last_in_group=None)
        group_mommy.feedbackset_new_attempt_published(group=feedbackset.group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_no_redirect_on_last_feedbackset_published(self):
        group = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_published(group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized,
                          examiner.assignmentgroup.assignment.get_path())

    def test_redirect_on_last_feedbackset_unpublished(self):
        group = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_unpublished(group=examiner.assignmentgroup)
        mockresponse = self.mock_getrequest(cradmin_role=examiner.assignmentgroup)
        self.assertEquals(302, mockresponse.response.status_code)

    def test_redirect_on_last_feedbackset_unpublished_multiple_feedbacksets(self):
        group = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_published(group=examiner.assignmentgroup, is_last_in_group=None)
        group_mommy.feedbackset_new_attempt_published(group=examiner.assignmentgroup, is_last_in_group=None)
        group_mommy.feedbackset_new_attempt_unpublished(group=examiner.assignmentgroup)
        mockresponse = self.mock_getrequest(cradmin_role=examiner.assignmentgroup)
        self.assertEquals(302, mockresponse.response.status_code)

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

    def test_feedbackset_created_with_published_feedbackset_without_comment(self):
        group = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_published(group=examiner.assignmentgroup)

        timestr = (datetimeutils.get_current_datetime() + timezone.timedelta(days=2)).strftime('%Y-%m-%d %H:%M')

        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': examiner.assignmentgroup.id},
            requestkwargs={
                'data': {
                    'deadline_datetime': timestr,
                    'text': '',
                    'examiner_create_new_feedbackset': 'unused value',
                }
            })

        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertEquals(3, len(feedbacksets))
        self.assertEquals(datetime.strptime(timestr, '%Y-%m-%d %H:%M'), feedbacksets[2].deadline_datetime)

        group_comments = group_models.GroupComment.objects.all()
        self.assertEquals(0, len(group_comments))

    def test_feedbackset_created_with_published_feedbackset_with_comment(self):
        group = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_published(group=examiner.assignmentgroup,
                                                        grading_published_by=examiner.relatedexaminer.user)

        timestr = (datetimeutils.get_current_datetime() + timezone.timedelta(days=2)).strftime('%Y-%m-%d %H:%M')
        comment_text = 'New attempt given'

        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': examiner.assignmentgroup.id},
            requestkwargs={
                'data': {
                    'deadline_datetime': timestr,
                    'text': comment_text,
                    'examiner_create_new_feedbackset': 'unused value',
                }
            })

        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertEquals(3, len(feedbacksets))
        self.assertEquals(datetime.strptime(timestr, '%Y-%m-%d %H:%M'), feedbacksets[2].deadline_datetime)

        comments = group_models.GroupComment.objects.all()
        self.assertEquals(1, len(comments))
        self.assertEquals(comments[0].feedback_set_id, feedbacksets[2].id)
        self.assertEquals(comments[0].text, comment_text)
