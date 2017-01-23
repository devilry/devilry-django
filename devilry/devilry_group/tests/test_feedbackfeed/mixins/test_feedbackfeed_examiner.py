from django.utils import timezone
from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_group import models as group_models
from devilry.devilry_group.models import GroupComment
from devilry.devilry_group.tests.test_feedbackfeed.mixins import test_feedbackfeed_common
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy


class TestFeedbackfeedExaminerMixin(test_feedbackfeed_common.TestFeedbackFeedMixin):
    """
    General mixin testclass with tests that should work on all examiner feedback views.
    """
    def test_get(self):
        examiner = mommy.make('core.Examiner')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized,
                          examiner.assignmentgroup.assignment.get_path())

    def test_get_feedbackfeed_anonymous_student_semi(self):
        testassignment = mommy.make('core.Assignment',
                                    anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = mommy.make('core.Candidate',
                               assignment_group=group,
                               relatedstudent__automatic_anonymous_id='AnonymousStudent',
                               relatedstudent__user__shortname='teststudent')
        mommy.make('devilry_group.GroupComment',
                   user_role='student',
                   user=candidate.relatedstudent.user,
                   feedback_set=group.feedbackset_set.first())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertFalse(mockresponse.selector.exists('.devilry-user-verbose-inline'))
        self.assertTrue(mockresponse.selector.exists('.devilry-core-candidate-anonymous-name'))
        self.assertEqual('AnonymousStudent',
                         mockresponse.selector.one('.devilry-core-candidate-anonymous-name').alltext_normalized)

    def test_get_feedbackfeed_anonymous_student_fully(self):
        testassignment = mommy.make('core.Assignment',
                                    anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = mommy.make('core.Candidate',
                               assignment_group=group,
                               relatedstudent__automatic_anonymous_id='AnonymousStudent',
                               relatedstudent__user__shortname='teststudent')
        mommy.make('devilry_group.GroupComment',
                   user_role='student',
                   user=candidate.relatedstudent.user,
                   feedback_set=group.feedbackset_set.first())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertFalse(mockresponse.selector.exists('.devilry-user-verbose-inline'))
        self.assertTrue(mockresponse.selector.exists('.devilry-core-candidate-anonymous-name'))
        self.assertEqual('AnonymousStudent',
                         mockresponse.selector.one('.devilry-core-candidate-anonymous-name').alltext_normalized)

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

    def test_get_examiner_can_see_student_comment(self):
        group = mommy.make('core.AssignmentGroup')
        student = mommy.make('core.Candidate',
                             assignment_group=group,
                             relatedstudent=mommy.make('core.RelatedStudent', user__fullname='Jane Doe'),)
        examiner = mommy.make('core.Examiner', assignmentgroup=group)
        mommy.make('devilry_group.GroupComment',
                   user=student.relatedstudent.user,
                   user_role='student',
                   published_datetime=timezone.now() - timezone.timedelta(days=1),
                   feedback_set=group.feedbackset_set.first())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(student.relatedstudent.user.fullname, name)

    def test_get_feedbackfeed_examiner_can_see_other_examiner_comment_visible_to_everyone(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        request_examiner = mommy.make('core.Examiner',
                                      assignmentgroup=group,
                                      relatedexaminer=mommy.make('core.RelatedExaminer'))
        comment_examiner = mommy.make('core.Examiner',
                                      assignmentgroup=group,
                                      relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='Jane Doe'))
        mommy.make('devilry_group.GroupComment',
                   user=comment_examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=timezone.now(),
                   feedback_set=group.feedbackset_set.first())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=request_examiner.assignmentgroup,
                                                          requestuser=request_examiner.relatedexaminer.user)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(comment_examiner.relatedexaminer.user.fullname, name)

    def test_get_feedbackfeed_examiner_can_see_other_examiner_comment_visible_to_examiner_and_admins(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        request_examiner = mommy.make('core.Examiner',
                                      assignmentgroup=group,
                                      relatedexaminer=mommy.make('core.RelatedExaminer'))
        comment_examiner = mommy.make('core.Examiner',
                                      assignmentgroup=group,
                                      relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='Jane Doe'))
        mommy.make('devilry_group.GroupComment',
                   user=comment_examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   published_datetime=timezone.now(),
                   feedback_set=group.feedbackset_set.first())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=request_examiner.assignmentgroup,
                                                          requestuser=request_examiner.relatedexaminer.user)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(comment_examiner.relatedexaminer.user.fullname, name)

    def test_get_feedbackfeed_other_examiner_can_not_see_comment_visibility_private(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        requestexaminer = mommy.make('core.Examiner',
                                     assignmentgroup=group,
                                     relatedexaminer=mommy.make('core.RelatedExaminer'))
        comment_post_examiner = mommy.make('core.Examiner',
                                           assignmentgroup=group,
                                           relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='Jane Doe'))
        mommy.make('devilry_group.GroupComment',
                   user=comment_post_examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   part_of_grading=True,
                   published_datetime=timezone.now(),
                   feedback_set=group.feedbackset_set.first())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group,
                                                          requestuser=requestexaminer.relatedexaminer.user)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))

    def test_get_feedbackfeed_examiner_can_see_own_private_comment(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   part_of_grading=True,
                   published_datetime=timezone.now(),
                   feedback_set=group.feedbackset_set.first())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))

    def test_get_examiner_can_not_see_other_examiner_comment_part_of_grading_private(self):
        group = mommy.make('core.AssignmentGroup')
        request_examiner = mommy.make('core.Examiner',
                                      assignmentgroup=group,
                                      relatedexaminer=mommy.make('core.RelatedExaminer'),)
        comment_examiner = mommy.make('core.Examiner',
                                      assignmentgroup=group,
                                      relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='Jane Doe'),)
        mommy.make('devilry_group.GroupComment',
                   user=comment_examiner.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   visibility=GroupComment.VISIBILITY_PRIVATE,
                   published_datetime=timezone.now() - timezone.timedelta(days=1),
                   feedback_set=group.feedbackset_set.first())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=request_examiner.assignmentgroup,
                                                          requestuser=request_examiner.relatedexaminer.user)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))

    def test_get_examiner_delete_on_drafts(self):
        group = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'),)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   visibility=GroupComment.VISIBILITY_PRIVATE,
                   feedback_set=group.feedbackset_set.first())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('.devilry-feedbackfeed-groupcomment-draft-delete'))
        self.assertTrue('Delete', mockresponse.selector.one('.devilry-feedbackfeed-groupcomment-draft-delete').alltext_normalized)

    def test_get_examiner_edit_on_drafts(self):
        group = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'),)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   part_of_grading=True,
                   visibility=GroupComment.VISIBILITY_PRIVATE,
                   feedback_set=group.feedbackset_set.first())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('.devilry-feedbackfeed-groupcomment-draft-edit'))
        self.assertTrue('Edit',
                        mockresponse.selector.one('.devilry-feedbackfeed-groupcomment-draft-edit').alltext_normalized)

    def test_get_examiner_first_attempt_unpublished_alert_choice_box_does_not_exist(self):
        # Tests that box providing the possibility of giving a new attempt or re-edit does NOT show when last
        # feedbackset has been NOT been published.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           grading_system_plugin_id=core_models.Assignment
                                           .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user
        )
        self.assertFalse(
            mockresponse.selector.exists('.devilry-group-feedbackfeed-examiner-after-publish-choice-alert'))

    def test_get_examiner_first_attempt_published_choice_alert_box_exists(self):
        # Tests that box providing the possibility of giving a new attempt shows when last feedbackset has been
        # published
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           grading_system_plugin_id=core_models.Assignment
                                           .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user
        )
        self.assertTrue(
            mockresponse.selector.exists('.devilry-group-feedbackfeed-examiner-after-publish-choice-alert'))

    def test_get_examiner_first_attempt_published_choice_alert_info_text(self):
        # Test the info-text in the alert box that show when the last feedbackset is published.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           grading_system_plugin_id=core_models.Assignment
                                           .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user
        )
        choice_alert_info_text = mockresponse.selector.one(
            '.devilry-group-feedbackfeed-examiner-after-publish-choice-alert-info-text'
        ).alltext_normalized
        self.assertEquals(
            'The first attempt has been graded. You can leave this grade '
            'as their final grade for this assignment, or:',
            choice_alert_info_text
        )

    def test_get_examiner_first_attempt_published_choice_alert_new_attempt_button(self):
        # Test that new attempt button exists in the choice alert when last feedbackset is published.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           grading_system_plugin_id=core_models.Assignment
                                           .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user
        )
        self.assertTrue(
            mockresponse.selector.exists(
                '.devilry-group-feedbackfeed-examiner-after-publish-choice-alert-new-attempt-button')
        )
        button_text = mockresponse.selector \
            .one(
            '.devilry-group-feedbackfeed-examiner-after-publish-choice-alert-new-attempt-button').alltext_normalized
        self.assertEquals('Give new attempt', button_text)

    def test_get_examiner_first_attempt_published_choice_alert_re_edit_button_text(self):
        # Test that new attempt button exists in the choice alert when last feedbackset is published.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           grading_system_plugin_id=core_models.Assignment
                                           .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user
        )
        self.assertTrue(
            mockresponse.selector.exists(
                '.devilry-group-feedbackfeed-examiner-after-publish-choice-alert-reedit-button')
        )
        button_text = mockresponse.selector \
            .one('.devilry-group-feedbackfeed-examiner-after-publish-choice-alert-reedit-button').alltext_normalized
        self.assertEquals('Edit the grade', button_text)

    def test_get_examiner_new_attempt_unpublished_choice_alert_does_not_exist(self):
        # Test that choice alert for giving a new attempt or re editing the last does NOT show
        # when first feedbackset is published, but the new try is unpublished.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           grading_system_plugin_id=core_models.Assignment
                                           .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        testfeedbackset_new_attempt = group_mommy.feedbackset_new_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user
        )
        self.assertNotEquals(testgroup.cached_data.last_published_feedbackset, testfeedbackset_new_attempt)
        self.assertEquals(testgroup.cached_data.last_feedbackset, testfeedbackset_new_attempt)
        self.assertFalse(
            mockresponse.selector.exists('.devilry-group-feedbackfeed-examiner-after-publish-choice-alert')
        )

    def test_get_examiner_new_attempt_published_choice_alert_exists(self):
        # Tests that choice alert for giving new attempt or re editing the last shows
        # when first feedbackset and new attempt is published.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           grading_system_plugin_id=core_models.Assignment
                                           .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        testfeedbackset_new_attempt = group_mommy.feedbackset_new_attempt_published(group=testgroup)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user
        )
        self.assertEquals(testgroup.cached_data.last_published_feedbackset, testfeedbackset_new_attempt)
        self.assertEquals(testgroup.cached_data.last_feedbackset, testfeedbackset_new_attempt)
        self.assertTrue(
            mockresponse.selector.exists('.devilry-group-feedbackfeed-examiner-after-publish-choice-alert')
        )

    def test_post_comment_always_to_last_feedbackset(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment
                                       .GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        feedbackset_first = group_mommy.feedbackset_first_attempt_published(group=group)
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
        self.assertEquals(2, group_models.FeedbackSet.objects.count())

    def test_get_num_queries(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=testfeedbackset,
                   _quantity=100)

        with self.assertNumQueries(13):
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
        candidate = mommy.make('core.Candidate', assignment_group=testgroup)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup)
        comment = mommy.make('devilry_group.GroupComment',
                             user=examiner.relatedexaminer.user,
                             user_role='examiner',
                             feedback_set=testfeedbackset)
        comment2 = mommy.make('devilry_group.GroupComment',
                              user=examiner.relatedexaminer.user,
                              user_role='examiner',
                              feedback_set=testfeedbackset)
        mommy.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role='student',
                   feedback_set=testfeedbackset,
                   _quantity=20)
        mommy.make('devilry_comment.CommentFile',
                   filename='test.py',
                   comment=comment,
                   _quantity=100)
        mommy.make('devilry_comment.CommentFile',
                   filename='test2.py',
                   comment=comment2,
                   _quantity=100)
        with self.assertNumQueries(13):
            self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                               requestuser=examiner.relatedexaminer.user)
