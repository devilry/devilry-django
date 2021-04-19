from django.core.exceptions import PermissionDenied
from django.test import TestCase
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import models as group_models
from devilry.devilry_group.views.examiner import feedbackfeed_examiner


class TestFeedbackFeedDeleteComment(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = feedbackfeed_examiner.GroupCommentDeleteView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_delete_comment_draft(self):
        # Test that the GroupComment does not exist after delete is posted
        group = baker.make('core.AssignmentGroup')
        examiner = baker.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=baker.make('core.RelatedExaminer'))

        comment = baker.make('devilry_group.GroupComment',
                             user=examiner.relatedexaminer.user,
                             user_role='examiner',
                             part_of_grading=True,
                             visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                             feedback_set=group.feedbackset_set.first())

        self.assertEqual(1, len(group_models.GroupComment.objects.all()))

        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': comment.id})

        self.assertEqual(0, len(group_models.GroupComment.objects.all()))

    def test_delete_comment_is_not_draft(self):
        # Test that PermissionDenied(403) is raised when trying to delete a non-draft GroupComment.
        testexaminer = baker.make('core.Examiner',
                                  relatedexaminer=baker.make('core.RelatedExaminer'))
        testcomment = baker.make('devilry_group.GroupComment',
                                 user=testexaminer.relatedexaminer.user,
                                 user_role='examiner',
                                 feedback_set=testexaminer.assignmentgroup.feedbackset_set.first())
        with self.assertRaises(PermissionDenied):
            self.mock_getrequest(cradmin_role=testexaminer.assignmentgroup,
                                 requestuser=testexaminer.relatedexaminer.user,
                                 viewkwargs={'pk': testcomment.id})

    def test_delete_comment_only_created_by_requestuser(self):
        # Test that another examiner cannot delete other examiners drafts.
        testexaminer = baker.make('core.Examiner',
                                  relatedexaminer=baker.make('core.RelatedExaminer'))
        testexaminer_author = baker.make('core.Examiner',
                                         assignmentgroup=testexaminer.assignmentgroup,
                                         relatedexaminer=baker.make('core.RelatedExaminer'))
        testcommentdraft = baker.make('devilry_group.GroupComment',
                                      user=testexaminer_author.relatedexaminer.user,
                                      user_role='examiner',
                                      part_of_grading=True,
                                      visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                                      feedback_set=testexaminer.assignmentgroup.feedbackset_set.first())
        with self.assertRaises(PermissionDenied):
            self.mock_getrequest(cradmin_role=testexaminer.assignmentgroup,
                                 requestuser=testexaminer.relatedexaminer.user,
                                 viewkwargs={'pk': testcommentdraft.id})

    def test_delete_and_cancel_buttons_exists(self):
        # Test that `Delete` and `Cancel` buttons exist
        testexaminer = baker.make('core.Examiner',
                                  relatedexaminer=baker.make('core.RelatedExaminer'))
        testcomment = baker.make('devilry_group.GroupComment',
                                 user=testexaminer.relatedexaminer.user,
                                 user_role='examiner',
                                 part_of_grading=True,
                                 visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                                 feedback_set=testexaminer.assignmentgroup.feedbackset_set.first())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testexaminer.assignmentgroup,
                                                          requestuser=testexaminer.relatedexaminer.user,
                                                          viewkwargs={'pk': testcomment.id})
        self.assertEqual('Delete', mockresponse.selector.one('.btn-danger').alltext_normalized)
        self.assertEqual('Cancel', mockresponse.selector.one('.btn-cancel').alltext_normalized)

    def test_delete_num_queries(self):
        # Test number of queries executed
        testexaminer = baker.make('core.Examiner',
                                  relatedexaminer=baker.make('core.RelatedExaminer'))
        testcomment = baker.make('devilry_group.GroupComment',
                                 user=testexaminer.relatedexaminer.user,
                                 user_role='examiner',
                                 part_of_grading=True,
                                 visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                                 feedback_set=testexaminer.assignmentgroup.feedbackset_set.first())
        with self.assertNumQueries(2):
            self.mock_http200_getrequest_htmls(cradmin_role=testexaminer.assignmentgroup,
                                               requestuser=testexaminer.relatedexaminer.user,
                                               viewkwargs={'pk': testcomment.id})
