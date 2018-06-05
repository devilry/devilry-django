from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.test import TestCase
from django.utils import timezone
from django.conf import settings
from django.core import mail
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_dbcache import models as cache_models
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models as group_models
from devilry.devilry_group.tests.test_feedbackfeed.mixins import test_feedbackfeed_examiner
from devilry.devilry_group.views.examiner import feedbackfeed_examiner
from devilry.devilry_comment import models as comment_models


class TestFeedbackfeedExaminerFeedback(TestCase, test_feedbackfeed_examiner.TestFeedbackfeedExaminerMixin):
    """
    Tests the general function of the ExaminerFeedbackView.
    """
    viewclass = feedbackfeed_examiner.ExaminerFeedbackView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_no_404_on_last_feedbackset_unpublished(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_getrequest(cradmin_role=examiner.assignmentgroup,
                                            requestuser=examiner.relatedexaminer.user)
        self.assertEquals(mockresponse.response.status_code, 200)

    def test_404_on_last_feedbackset_published(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        with self.assertRaises(Http404):
            self.mock_getrequest(
                cradmin_role=examiner.assignmentgroup,
                requestuser=examiner.relatedexaminer.user)

    def test_get_feedbackfeed_examiner_can_see_feedback_and_discuss_in_comment_tab(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-feedback-button'))
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-discuss-button'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choice_add_comment_for_examiners_and_admins_button(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_publish_feedback'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choice_add_comment_to_feedbackdraft_button(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
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
        mommy.make('core.Candidate', assignment_group=testgroup, _quantity=50)
        mommy.make('core.Examiner', assignmentgroup=testgroup, _quantity=50)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        candidate = mommy.make('core.Candidate', assignment_group=testgroup)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=testfeedbackset,
                   _quantity=20)
        mommy.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role='student',
                   feedback_set=testfeedbackset,
                   _quantity=20)
        with self.assertNumQueries(19):
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
        mommy.make('core.Candidate', assignment_group=testgroup, _quantity=50)
        mommy.make('core.Examiner', assignmentgroup=testgroup, _quantity=50)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        candidate = mommy.make('core.Candidate', assignment_group=testgroup)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=testfeedbackset,
                   _quantity=20)
        mommy.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role='student',
                   feedback_set=testfeedbackset,
                   _quantity=20)
        comment = mommy.make('devilry_group.GroupComment',
                             user=examiner.relatedexaminer.user,
                             user_role='examiner',
                             feedback_set=testfeedbackset)
        comment2 = mommy.make('devilry_group.GroupComment',
                              user=candidate.relatedstudent.user,
                              user_role='student',
                              feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile',
                   filename='test.py',
                   comment=comment,
                   _quantity=20)
        mommy.make('devilry_comment.CommentFile',
                   filename='test2.py',
                   comment=comment2,
                   _quantity=20)
        with self.assertNumQueries(19):
            self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                               requestuser=examiner.relatedexaminer.user)

    def test_post_feedbackdraft_comment_with_text(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active'))
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
                    'passed': 'Passed',
                    'text': 'This is a comment',
                    'examiner_add_comment_to_feedback_draft': 'unused value'
                }
            })
        group_comment = group_models.GroupComment.objects.all()[0]
        self.assertEquals(group_comment.visibility, group_models.GroupComment.VISIBILITY_PRIVATE)

    def test_get_feedbackset_deadline_history_semi_anonymous_username_not_rendered(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='test@example.com', fullname='Test User')
        mommy.make('devilry_group.FeedbackSetDeadlineHistory', feedback_set=testgroup.cached_data.first_feedbackset,
                   changed_by=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup
        )
        self.assertFalse(
            mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message__user_display_name'))

    def test_get_feedbackset_deadline_history_fully_anonymous_username_not_rendered(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='test@example.com', fullname='Test User')
        mommy.make('devilry_group.FeedbackSetDeadlineHistory', feedback_set=testgroup.cached_data.first_feedbackset,
                   changed_by=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup
        )
        self.assertFalse(
            mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message__user_display_name'))


class TestFeedbackFeedExaminerPublishFeedback(TestCase, test_feedbackfeed_examiner.TestFeedbackfeedExaminerMixin):
    """
    Explicitly tests creating drafts and publishing of the FeedbackSet.
    """
    viewclass = feedbackfeed_examiner.ExaminerFeedbackView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_post_first_attempt_draft_appear_before_grading_event(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner', assignmentgroup=testfeedbackset.group)
        mommy.make(
            'devilry_group.GroupComment',
            feedback_set=testfeedbackset,
            user=examiner.relatedexaminer.user,
            user_role='examiner',
            part_of_grading=True)
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'passed': 'Failed',
                    'text': '',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user
        )
        class_list = [list(item.cssclasses_set) for item in
                      mockresponse.selector.list('.devilry-group-feedbackfeed-itemvalue')]
        # Test that grade comments are rendered before grade
        self.assertIn('devilry-group-feedbackfeed-comment-examiner', class_list[1])
        self.assertIn('devilry-group-feedbackfeed-event-message__grade', class_list[2])

    def test_post_first_attempt_two_drafts_appear_before_grading_event(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner', assignmentgroup=testfeedbackset.group)

        # Draft created before publish
        mommy.make(
            'devilry_group.GroupComment',
            feedback_set=testfeedbackset,
            user=examiner.relatedexaminer.user,
            user_role='examiner',
            text='Draft',
            part_of_grading=True)

        # Publish with comment
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'passed': 'Passed',
                    'text': 'Corrected',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user
        )
        class_list = [list(item.cssclasses_set) for item in
                      mockresponse.selector.list('.devilry-group-feedbackfeed-itemvalue')]

        # Test that grade comments are rendered before grade
        self.assertIn('devilry-group-feedbackfeed-comment-examiner', class_list[1])
        self.assertIn('devilry-group-feedbackfeed-comment-examiner', class_list[2])
        self.assertIn('devilry-group-feedbackfeed-event-message__grade', class_list[3])

    def test_post_first_attempt_draft_occurs_before_comment_published(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner', assignmentgroup=testfeedbackset.group)

        # Draft created before publish
        mommy.make(
            'devilry_group.GroupComment',
            feedback_set=testfeedbackset,
            user=examiner.relatedexaminer.user,
            user_role='examiner',
            text='Draft',
            part_of_grading=True)

        # Publish with comment
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'passed': 'Passed',
                    'text': 'Corrected',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user
        )
        comment_text_elements = mockresponse.selector.list('.devilry-group-comment-text')
        self.assertEquals('Draft', comment_text_elements[0].alltext_normalized)
        self.assertEquals('Corrected', comment_text_elements[1].alltext_normalized)

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
                    'passed': 'Passed',
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
                    'passed': 'Passed',
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
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent=mommy.make('core.RelatedStudent'))
        comment1 = mommy.make('devilry_group.GroupComment',
                   text='test text 1',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   feedback_set=feedbackset_first)
        feedback_comment = mommy.make('devilry_group.GroupComment',
                                      text='part of grading',
                                      user=examiner.relatedexaminer.user,
                                      user_role='examiner',
                                      part_of_grading=True,
                                      feedback_set=feedbackset_last)
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': testgroup.id},
            requestkwargs={
                'data': {
                    'passed': 'Passed',
                    'text': 'post comment',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        feedback_comments = group_models.GroupComment.objects.all()\
            .filter(feedback_set_id=cached_group.last_published_feedbackset.id)\
            .order_by('published_datetime')
        self.assertEqual(2, len(feedback_comments))
        self.assertEqual(feedback_comments[0].text, 'part of grading')
        self.assertEqual(feedback_comments[1].text, 'post comment')
        self.assertEqual(cached_group.last_published_feedbackset, feedbackset_last)

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
                    'passed': 'Passed',
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
                    'passed': 'Passed',
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
                    'passed': 'Passed',
                    'text': 'test',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        cached_group = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        self.assertEquals(cached_group.last_published_feedbackset, feedbackset)
        self.assertIsNotNone(cached_group.last_published_feedbackset.grading_published_datetime)
        self.assertEquals(1, group_models.GroupComment.objects.all().count())
        self.assertEquals('test', group_models.GroupComment.objects.get(feedback_set=feedbackset).text)

    def test_examiner_publishes_email_is_sent(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
                                       points_to_grade_mapper=core_models.Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
                                       max_points=100,
                                       passing_grade_min_points=50,
                                       long_name='Assignment 1',
                                       parentnode__parentnode__long_name='Duck 1010')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=30))
        examiner_user = mommy.make(settings.AUTH_USER_MODEL, fullname='God of thunder and Battle',
                                   shortname='thor@example.com')
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer', user=examiner_user))
        student_user = mommy.make(settings.AUTH_USER_MODEL, shortname='student')
        mommy.make('devilry_account.UserEmail', email='student@example.com', user=student_user)
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent=mommy.make('core.RelatedStudent', user=student_user))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'points': 73,
                    'examiner_publish_feedback': 'unused value',
                }
            })
        mail_content = mail.outbox[0].message().as_string()
        self.assertIn('Assignment: {}'.format(assignment.long_name), mail_content)
        self.assertIn('Subject: {}'.format(assignment.parentnode.parentnode.long_name), mail_content)
        self.assertIn('Result: 73/100 ( passed )', mail_content)
        self.assertIn('http://testserver/devilry_group/student/{}/feedbackfeed/'.format(testgroup.id), mail_content)
        self.assertEqual(mail.outbox[0].recipients(), ['student@example.com'])
        self.assertEqual(len(mail.outbox), 1)


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
                    'passed': 'Passed',
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
                    'passed': 'Passed',
                    'text': '',
                    'examiner_add_comment_to_feedback_draft': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(2, comment_models.CommentFile.objects.count())
        self.assertEqual(1, group_models.GroupComment.objects.count())
        self.assertIsNone(group_models.FeedbackSet.objects.get(id=testfeedbackset.id).grading_published_datetime)
