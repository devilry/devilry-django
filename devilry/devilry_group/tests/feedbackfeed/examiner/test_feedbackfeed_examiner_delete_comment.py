from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_group import models as group_models
from devilry.devilry_group.views.examiner import feedbackfeed_examiner


class TestFeedbackFeedDeleteComment(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = feedbackfeed_examiner.GroupCommentDeleteView

    def test_delete_comment_draft(self):
        # Test that the GroupComment does not exist after delete is posted
        group = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))

        comment = mommy.make('devilry_group.GroupComment',
                             user=examiner.relatedexaminer.user,
                             user_role='examiner',
                             part_of_grading=True,
                             visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                             feedback_set__group=group)

        self.assertEquals(1, len(group_models.GroupComment.objects.all()))

        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': comment.id})

        self.assertEquals(0, len(group_models.GroupComment.objects.all()))

    def test_delete_comment_is_not_draft(self):
        # Test that PermissionDenied(403) is raised when trying to delete a non-draft GroupComment.
        testexaminer = mommy.make('core.Examiner',
                                  relatedexaminer=mommy.make('core.RelatedExaminer'))
        testcomment = mommy.make('devilry_group.GroupComment',
                                 user=testexaminer.relatedexaminer.user,
                                 user_role='examiner',
                                 feedback_set__group=testexaminer.assignmentgroup)
        with self.assertRaises(PermissionDenied):
            self.mock_getrequest(cradmin_role=testexaminer.assignmentgroup,
                                 requestuser=testexaminer.relatedexaminer.user,
                                 viewkwargs={'pk': testcomment.id})

    def test_delete_and_cancel_buttons_exists(self):
        # Test that `Delete` and `Cancel` buttons exist
        testexaminer = mommy.make('core.Examiner',
                                  relatedexaminer=mommy.make('core.RelatedExaminer'))
        testcomment = mommy.make('devilry_group.GroupComment',
                                 user=testexaminer.relatedexaminer.user,
                                 user_role='examiner',
                                 part_of_grading=True,
                                 visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                                 feedback_set__group=testexaminer.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testexaminer.assignmentgroup,
                                                          requestuser=testexaminer.relatedexaminer.user,
                                                          viewkwargs={'pk': testcomment.id})
        self.assertEquals('Delete', mockresponse.selector.one('.btn-danger').alltext_normalized)
        self.assertEquals('Cancel', mockresponse.selector.one('.btn-cancel').alltext_normalized)
