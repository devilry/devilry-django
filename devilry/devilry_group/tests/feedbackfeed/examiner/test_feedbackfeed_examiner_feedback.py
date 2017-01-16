import unittest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_dbcache import models as cache_models
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models as group_models
from devilry.devilry_group.tests.feedbackfeed.mixins import test_feedbackfeed_examiner
from devilry.devilry_group.views.examiner import feedbackfeed_examiner
from devilry.devilry_comment import models as comment_models


class TestFeedbackfeedExaminerFeedback(TestCase, test_feedbackfeed_examiner.TestFeedbackfeedExaminerMixin):
    """
    Tests the general function of the ExaminerFeedbackView.
    """
    viewclass = feedbackfeed_examiner.ExaminerFeedbackView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_no_redirect_on_last_feedbackset_unpublished(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_getrequest(cradmin_role=examiner.assignmentgroup,
                                            requestuser=examiner.relatedexaminer.user)
        self.assertEquals(mockresponse.response.status_code, 200)

    def test_redirect_on_last_feedbackset_published(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        mockresponse = self.mock_getrequest(cradmin_role=examiner.assignmentgroup,
                                            requestuser=examiner.relatedexaminer.user)
        self.assertEquals(mockresponse.response.status_code, 302)

    def test_get_feedbackset_first_no_created_deadline_event(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testfeedbackset.group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_get_feedbackset_second_created_deadline_event(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        group_mommy.feedbackset_new_attempt_unpublished(group=testgroup)
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
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_publish_feedback'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_to_feedbackdraft_button(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_add_comment_to_feedback_draft'))

    def test_get_form_passedfailed_grade_option(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment
                                       .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#div_id_passed'))
        self.assertFalse(mockresponse.selector.exists('#div_id_points'))

    def test_get_form_points_grade_option(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertFalse(mockresponse.selector.exists('#div_id_passed'))
        self.assertTrue(mockresponse.selector.exists('#div_id_points'))

    def test_get_num_queries(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
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
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
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

    def test_post_feedbackdraft_comment_with_text(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
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

    def test_post_feedbackset_comment_visibility_private(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
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
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
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
        self.assertEquals(1, group_models.FeedbackSet.objects.all().count())
        self.assertIsNone(group_models.FeedbackSet.objects.all()[0].grading_published_datetime)
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        self.assertIsNone(cached_group.last_published_feedbackset)

    @unittest.skip('Should most likely be removed. The DB triggers enforce that only the first '
                   'feedbackset can have deadline_datetime=None.')
    def test_post_can_not_publish_with_last_feedbackset_deadline_as_none(self):
        assignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset_first = group_mommy.feedbackset_first_attempt_published(group=testgroup)
        group_mommy.feedbackset_new_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all().order_by('created_datetime')
        self.assertEquals(2, len(feedbacksets))
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
        self.assertIsNone(feedbacksets[1].grading_published_datetime)
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        self.assertEquals(cached_group.last_published_feedbackset, testfeedbackset_first)

    def test_post_can_not_publish_feedbackset_before_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_middle')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
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
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        self.assertIsNone(cached_group.last_published_feedbackset)

    def test_post_publish_feedbackset_after_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
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
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        self.assertEquals(cached_group.last_published_feedbackset, feedbackset)

    def test_post_publish_feedbackset_after_deadline_grading_system_points(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
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
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
        self.assertEquals(10, feedbacksets[0].grading_points)
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        self.assertEquals(cached_group.last_published_feedbackset, feedbackset)

    def test_post_publish_feedbackset_after_deadline_grading_system_passed_failed(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment
                                       .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
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
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
        self.assertEquals(1, feedbacksets[0].grading_points)
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        self.assertEquals(cached_group.last_published_feedbackset, feedbackset)

    def test_post_publish_feedbackset_drafts_on_last_feedbackset_only(self):
        assignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset_first = group_mommy.feedbackset_first_attempt_published(group=testgroup)
        feedbackset_last = group_mommy.feedbackset_new_attempt_unpublished(
                group=testgroup,
                deadline_datetime=timezone.now() - timezone.timedelta(days=1))
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        student = mommy.make('core.Candidate',
                             assignment_group=testgroup,
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
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': 'post comment',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        feedback_comments = group_models.GroupComment.objects.all().filter(
                feedback_set=cached_group.last_published_feedbackset)

        self.assertEquals(2, len(feedback_comments))
        self.assertEquals(feedback_comments[0], comment2)
        self.assertEquals(feedback_comments[1].text, 'post comment')
        self.assertEquals(cached_group.last_published_feedbackset, feedbackset_last)

    def test_post_publish_feedbackset_after_deadline_test_publish_drafts_part_of_grading(self):
        assignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
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
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        feedback_comments = group_models.GroupComment.objects.all()
        self.assertEquals(feedbackset, cached_group.last_published_feedbackset)
        self.assertIsNotNone(cached_group.last_published_feedbackset.grading_published_datetime)
        self.assertEquals(1, cached_group.last_published_feedbackset.grading_points)
        self.assertEquals(5, len(feedback_comments))

    def test_get_num_queries(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
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
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
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

    def test_examiner_publishes_without_comment_text(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment
                                       .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': '',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
        self.assertEquals(0, group_models.GroupComment.objects.count())
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        self.assertEquals(cached_group.last_published_feedbackset, feedbackset)

    def test_examiner_publishes_with_comment_text(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment
                                       .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': 'test',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        self.assertEquals(cached_group.last_published_feedbackset, feedbackset)
        self.assertIsNotNone(cached_group.last_published_feedbackset.grading_published_datetime)
        self.assertEquals(1, group_models.GroupComment.objects.all().count())
        self.assertEquals('test', group_models.GroupComment.objects.get(feedback_set=feedbackset).text)


class TestFeedbackfeedFeedbackFileUploadExaminer(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = feedbackfeed_examiner.ExaminerFeedbackView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_upload_files_publish(self):
        # Test the content of a CommentFile after upload.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           grading_system_plugin_id=core_models.Assignment
                                           .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=testassignment)
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt')
            ],
            user=testexaminer.relatedexaminer.user
        )
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': '',
                    'examiner_publish_feedback': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(2, comment_models.CommentFile.objects.count())
        self.assertEqual(1, group_models.GroupComment.objects.count())
        self.assertIsNotNone(group_models.FeedbackSet.objects.get(id=testfeedbackset.id).grading_published_datetime)

    def test_upload_files_draft(self):
        # Test the content of a CommentFile after upload.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           grading_system_plugin_id=core_models.Assignment
                                           .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=testassignment)
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt')
            ],
            user=testexaminer.relatedexaminer.user
        )
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': '',
                    'examiner_add_comment_to_feedback_draft': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(2, comment_models.CommentFile.objects.count())
        self.assertEqual(1, group_models.GroupComment.objects.count())
        self.assertIsNone(group_models.FeedbackSet.objects.get(id=testfeedbackset.id).grading_published_datetime)


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
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_examiner_can_see_deadline_picker(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('#id_deadline_datetime_triggerbutton'))

    def test_examiner_can_only_see_create_new_feedbackset_button(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_create_new_feedbackset'))
        self.assertFalse(mockresponse.selector.exists('#submit-id-examiner_publish_feedback'))
        self.assertFalse(mockresponse.selector.exists('#submit-id-examiner_add_comment_to_feedback_draft'))

    def test_get_feedbackset_second_created_deadline_event(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup)
        group_mommy.feedbackset_new_attempt_published(group=feedbackset.group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.one('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_no_redirect_on_last_feedbackset_published(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized,
                          examiner.assignmentgroup.assignment.get_path())

    def test_redirect_on_last_feedbackset_unpublished(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_getrequest(cradmin_role=examiner.assignmentgroup)
        self.assertEquals(302, mockresponse.response.status_code)

    def test_redirect_on_last_feedbackset_unpublished_multiple_feedbacksets(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        group_mommy.feedbackset_new_attempt_published(group=testgroup)
        group_mommy.feedbackset_new_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_getrequest(cradmin_role=examiner.assignmentgroup)
        self.assertEquals(302, mockresponse.response.status_code)

    def test_get_feedbackfeed_event_delivery_passed(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       max_points=10,
                                       passing_grade_min_points=5)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_published(
                group=testgroup,
                grading_published_datetime=timezone.now(),
                grading_points=7)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-core-grade-passed'))

    def test_get_feedbackfeed_event_delivery_failed(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       max_points=10,
                                       passing_grade_min_points=5)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_published(
                group=testgroup,
                grading_published_datetime=timezone.now(),
                grading_points=3)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-core-grade-failed'))

    def test_feedbackset_created_with_published_feedbackset_without_comment(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__first_deadline=timezone.now() - timezone.timedelta(days=2))
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        deadline_datetime = timezone.now() + timezone.timedelta(days=2)
        deadline_datetime = deadline_datetime.replace(microsecond=0, second=0)

        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': examiner.assignmentgroup.id},
            requestkwargs={
                'data': {
                    'deadline_datetime': deadline_datetime.strftime('%Y-%m-%d %H:%M'),
                    'text': '',
                    'examiner_create_new_feedbackset': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.order_by_deadline_datetime()
        self.assertEquals(feedbacksets[1].deadline_datetime,
                          deadline_datetime)
        self.assertEquals(2, group_models.FeedbackSet.objects.count())
        group_comments = group_models.GroupComment.objects.all()
        self.assertEquals(0, len(group_comments))

    def test_feedbackset_created_with_published_feedbackset_with_comment(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__first_deadline=timezone.now() - timezone.timedelta(days=2))
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_published(group=testgroup,
                                                        grading_published_by=examiner.relatedexaminer.user)

        deadline_datetime = timezone.now() + timezone.timedelta(days=2)
        deadline_datetime = deadline_datetime.replace(microsecond=0, second=0)
        comment_text = 'New attempt given'

        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': examiner.assignmentgroup.id},
            requestkwargs={
                'data': {
                    'deadline_datetime': deadline_datetime.strftime('%Y-%m-%d %H:%M'),
                    'text': comment_text,
                    'examiner_create_new_feedbackset': 'unused value',
                }
            })

        feedbacksets = group_models.FeedbackSet.objects.order_by_deadline_datetime()
        self.assertEqual(2, group_models.FeedbackSet.objects.count())
        self.assertEquals(deadline_datetime, feedbacksets[1].deadline_datetime)

        comments = group_models.GroupComment.objects.all()
        self.assertEquals(1, len(comments))
        self.assertEquals(comments[0].feedback_set_id, feedbacksets[1].id)
        self.assertEquals(comments[0].text, comment_text)
        self.assertEquals(2, group_models.FeedbackSet.objects.count())


class TestFeedbackfeedCreateFeedbackSetFileUploadExaminer(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = feedbackfeed_examiner.ExaminerFeedbackCreateFeedbackSetView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_upload_single_file_on_feedbackset_create(self):
        # Test the content of a CommentFile after upload.
        # Posting comment with visibility visible to everyone
        testfeedbackset = group_mommy.feedbackset_first_attempt_published()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile.txt', content=b'Test content', content_type='text/txt')
            ],
            user=testexaminer.relatedexaminer.user
        )
        deadline_datetime = timezone.now() + timezone.timedelta(days=2)
        deadline_datetime = deadline_datetime.replace(microsecond=0, second=0)
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'deadline_datetime': deadline_datetime.strftime('%Y-%m-%d %H:%M'),
                    'text': '',
                    'examiner_create_new_feedbackset': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(2, group_models.FeedbackSet.objects.count())
        self.assertEquals(1, comment_models.CommentFile.objects.count())
        self.assertEqual(1, group_models.GroupComment.objects.count())

    def test_upload_single_file_content_on_feedbackset_create(self):
        # Test the content of a CommentFile after upload.
        # Posting comment with visibility visible to everyone
        testfeedbackset = group_mommy.feedbackset_first_attempt_published()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile.txt', content=b'Test content', content_type='text/txt')
            ],
            user=testexaminer.relatedexaminer.user
        )
        deadline_datetime = timezone.now() + timezone.timedelta(days=2)
        deadline_datetime = deadline_datetime.replace(microsecond=0, second=0)
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'deadline_datetime': deadline_datetime.strftime('%Y-%m-%d %H:%M'),
                    'text': '',
                    'examiner_create_new_feedbackset': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, comment_models.CommentFile.objects.count())
        self.assertEqual(1, group_models.GroupComment.objects.count())
        comment_file = comment_models.CommentFile.objects.all()[0]
        self.assertEqual('testfile.txt', comment_file.filename)
        self.assertEqual('Test content', comment_file.file.file.read())
        self.assertEqual(len('Test content'), comment_file.filesize)
        self.assertEqual('text/txt', comment_file.mimetype)

    def test_upload_multiple_files(self):
        # Test the content of a CommentFile after upload.
        testfeedbackset = group_mommy.feedbackset_first_attempt_published()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
                SimpleUploadedFile(name='testfile3.txt', content=b'Test content3', content_type='text/txt')
            ],
            user=testexaminer.relatedexaminer.user
        )
        deadline_datetime = timezone.now() + timezone.timedelta(days=2)
        deadline_datetime = deadline_datetime.replace(microsecond=0, second=0)
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'deadline_datetime': deadline_datetime.strftime('%Y-%m-%d %H:%M'),
                    'text': '',
                    'examiner_create_new_feedbackset': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(3, comment_models.CommentFile.objects.count())
        self.assertEqual(1, group_models.GroupComment.objects.count())

    def test_upload_multiple_files_contents(self):
        # Test the content of a CommentFile after upload.
        testfeedbackset = group_mommy.feedbackset_first_attempt_published()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
                SimpleUploadedFile(name='testfile3.txt', content=b'Test content3', content_type='text/txt')
            ],
            user=testexaminer.relatedexaminer.user
        )
        deadline_datetime = timezone.now() + timezone.timedelta(days=2)
        deadline_datetime = deadline_datetime.replace(microsecond=0, second=0)
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'deadline_datetime': deadline_datetime.strftime('%Y-%m-%d %H:%M'),
                    'text': '',
                    'examiner_create_new_feedbackset': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(3, comment_models.CommentFile.objects.count())
        comment_file1 = comment_models.CommentFile.objects.get(filename='testfile1.txt')
        comment_file2 = comment_models.CommentFile.objects.get(filename='testfile2.txt')
        comment_file3 = comment_models.CommentFile.objects.get(filename='testfile3.txt')

        # Check content of testfile 1.
        self.assertEqual('testfile1.txt', comment_file1.filename)
        self.assertEqual('Test content1', comment_file1.file.file.read())
        self.assertEqual(len('Test content1'), comment_file1.filesize)
        self.assertEqual('text/txt', comment_file1.mimetype)

        # Check content of testfile 2.
        self.assertEqual('testfile2.txt', comment_file2.filename)
        self.assertEqual('Test content2', comment_file2.file.file.read())
        self.assertEqual(len('Test content2'), comment_file2.filesize)
        self.assertEqual('text/txt', comment_file2.mimetype)

        # Check content of testfile 3.
        self.assertEqual('testfile3.txt', comment_file3.filename)
        self.assertEqual('Test content3', comment_file3.file.file.read())
        self.assertEqual(len('Test content3'), comment_file3.filesize)
        self.assertEqual('text/txt', comment_file3.mimetype)

    def test_upload_files_and_comment_text(self):
        # Test the content of a CommentFile after upload.
        testfeedbackset = group_mommy.feedbackset_first_attempt_published()
        testexaminer = mommy.make('core.examiner', assignmentgroup=testfeedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
            ],
            user=testexaminer.relatedexaminer.user
        )
        deadline_datetime = timezone.now() + timezone.timedelta(days=2)
        deadline_datetime = deadline_datetime.replace(microsecond=0, second=0)
        self.mock_http302_postrequest(
            cradmin_role=testexaminer.assignmentgroup,
            requestuser=testexaminer.relatedexaminer.user,
            viewkwargs={'pk': testfeedbackset.group.id},
            requestkwargs={
                'data': {
                    'deadline_datetime': deadline_datetime.strftime('%Y-%m-%d %H:%M'),
                    'text': 'Test comment',
                    'examiner_create_new_feedbackset': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(2, comment_models.CommentFile.objects.count())
        self.assertEqual(1, group_models.GroupComment.objects.count())
        group_comments = group_models.GroupComment.objects.all()
        self.assertEquals('Test comment', group_comments[0].text)
