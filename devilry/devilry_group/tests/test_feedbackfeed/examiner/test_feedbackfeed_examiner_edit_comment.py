from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import models as group_models
from devilry.devilry_group.views.examiner import feedbackfeed_examiner


class TestFeedbackFeedEditGroupComment(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = feedbackfeed_examiner.GroupCommentEditView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_edit_comment_draft_save(self):
        # Test that the GroupComment is updated after default save
        group = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))

        comment = mommy.make('devilry_group.GroupComment',
                             user=examiner.relatedexaminer.user,
                             user_role='examiner',
                             text='unedited',
                             part_of_grading=True,
                             visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                             feedback_set=group.feedbackset_set.first())
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': comment.id},
            requestkwargs={
                'data': {
                    'text': 'edited',
                    'submit-id-submit-save': 'True',
                }
            },
        )
        db_comment = group_models.GroupComment.objects.get(id=comment.id)
        self.assertEquals('edited', db_comment.text)

    def test_edit_comment_draft_save_continue_edit(self):
        # Test that the GroupComment is updated after 'Save and continue editing'
        group = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        comment = mommy.make('devilry_group.GroupComment',
                             user=examiner.relatedexaminer.user,
                             user_role='examiner',
                             text='unedited',
                             part_of_grading=True,
                             visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                             feedback_set=group.feedbackset_set.first())
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': comment.id},
            requestkwargs={
                'data': {
                    'text': 'edited',
                    'submit-save-and-continue-editing': 'True',
                }
            },
        )
        db_comment = group_models.GroupComment.objects.get(id=comment.id)
        self.assertEquals('edited', db_comment.text)

    def test_edit_comment_is_not_draft(self):
        # Test that PermissionDenied(403) is raised when trying to edit a non-draft GroupComment.
        testexaminer = mommy.make('core.Examiner',
                                  relatedexaminer=mommy.make('core.RelatedExaminer'))
        testcomment = mommy.make('devilry_group.GroupComment',
                                 user=testexaminer.relatedexaminer.user,
                                 user_role='examiner',
                                 feedback_set=testexaminer.assignmentgroup.feedbackset_set.first())
        with self.assertRaises(PermissionDenied):
            self.mock_getrequest(cradmin_role=testexaminer.assignmentgroup,
                                 requestuser=testexaminer.relatedexaminer.user,
                                 viewkwargs={'pk': testcomment.id})

    def test_edit_comment_only_created_by_requestuser(self):
        # Test that another examiner cannot edit other examiners drafts.
        testexaminer = mommy.make('core.Examiner',
                                  relatedexaminer=mommy.make('core.RelatedExaminer'))
        testexaminer_author = mommy.make('core.Examiner',
                                         assignmentgroup=testexaminer.assignmentgroup,
                                         relatedexaminer=mommy.make('core.RelatedExaminer'))
        testcommentdraft = mommy.make('devilry_group.GroupComment',
                                      user=testexaminer_author.relatedexaminer.user,
                                      user_role='examiner',
                                      part_of_grading=True,
                                      visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                                      feedback_set=testexaminer.assignmentgroup.feedbackset_set.first())
        with self.assertRaises(PermissionDenied):
            self.mock_getrequest(cradmin_role=testexaminer.assignmentgroup,
                                 requestuser=testexaminer.relatedexaminer.user,
                                 viewkwargs={'pk': testcommentdraft.id})

    def test_save_buttons_exist(self):
        # Test that the save buttons exist in the edit view.
        testexaminer = mommy.make('core.Examiner',
                                  relatedexaminer=mommy.make('core.RelatedExaminer'))
        testcomment = mommy.make('devilry_group.GroupComment',
                                 user=testexaminer.relatedexaminer.user,
                                 user_role='examiner',
                                 part_of_grading=True,
                                 visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                                 feedback_set=testexaminer.assignmentgroup.feedbackset_set.first())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testexaminer.assignmentgroup,
                                                          requestuser=testexaminer.relatedexaminer.user,
                                                          viewkwargs={'pk': testcomment.id})
        self.assertTrue(mockresponse.selector.exists('#submit-id-submit-save'))
        self.assertTrue(mockresponse.selector.exists('#submit-id-submit-save-and-continue-editing'))

    def test_edit_num_queries(self):
        # Test number of queries executed
        testexaminer = mommy.make('core.Examiner',
                                  relatedexaminer=mommy.make('core.RelatedExaminer'))
        testcomment = mommy.make('devilry_group.GroupComment',
                                 user=testexaminer.relatedexaminer.user,
                                 user_role='examiner',
                                 part_of_grading=True,
                                 visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                                 feedback_set=testexaminer.assignmentgroup.feedbackset_set.first())
        with self.assertNumQueries(2):
            self.mock_http200_getrequest_htmls(cradmin_role=testexaminer.assignmentgroup,
                                               requestuser=testexaminer.relatedexaminer.user,
                                               viewkwargs={'pk': testcomment.id})
