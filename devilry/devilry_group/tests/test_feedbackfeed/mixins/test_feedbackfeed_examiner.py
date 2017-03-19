from model_mommy import mommy

from django.utils import timezone

from devilry.apps.core import models as core_models
from devilry.devilry_group import models as group_models
from devilry.devilry_group.models import GroupComment
from devilry.devilry_group.tests.test_feedbackfeed.mixins import test_feedbackfeed_common


class TestFeedbackfeedExaminerMixin(test_feedbackfeed_common.TestFeedbackFeedMixin):
    """
    Mixin testclass for examiner feedbackfeed tests.

    Add tests for functionality and ui that all examiner views share.
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

    # def test_get_num_queries(self):
    #     testgroup = mommy.make('core.AssignmentGroup')
    #     examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
    #     testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
    #     mommy.make('devilry_group.GroupComment',
    #                user=examiner.relatedexaminer.user,
    #                user_role='examiner',
    #                feedback_set=testfeedbackset,
    #                _quantity=100)
    #
    #     with self.assertNumQueries(13):
    #         self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
    #                                            requestuser=examiner.relatedexaminer.user)
    #
    # def test_get_num_queries_with_commentfiles(self):
    #     """
    #     NOTE: (works as it should)
    #     Checking that no more queries are executed even though the
    #     :func:`devilry.devilry_group.feedbackfeed_builder.FeedbackFeedTimelineBuilder.__get_feedbackset_queryset`
    #     duplicates comment_file query.
    #     """
    #     testgroup = mommy.make('core.AssignmentGroup')
    #     examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
    #     candidate = mommy.make('core.Candidate', assignment_group=testgroup)
    #     testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
    #     comment = mommy.make('devilry_group.GroupComment',
    #                          user=examiner.relatedexaminer.user,
    #                          user_role='examiner',
    #                          feedback_set=testfeedbackset)
    #     comment2 = mommy.make('devilry_group.GroupComment',
    #                           user=examiner.relatedexaminer.user,
    #                           user_role='examiner',
    #                           feedback_set=testfeedbackset)
    #     mommy.make('devilry_group.GroupComment',
    #                user=candidate.relatedstudent.user,
    #                user_role='student',
    #                feedback_set=testfeedbackset,
    #                _quantity=20)
    #     mommy.make('devilry_comment.CommentFile',
    #                filename='test.py',
    #                comment=comment,
    #                _quantity=100)
    #     mommy.make('devilry_comment.CommentFile',
    #                filename='test2.py',
    #                comment=comment2,
    #                _quantity=100)
    #     with self.assertNumQueries(13):
    #         self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
    #                                            requestuser=examiner.relatedexaminer.user)
