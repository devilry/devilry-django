from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_group import models as group_models
from devilry.devilry_group.views.examiner import feedbackfeed_examiner


class TestFeedbackFeedEditGroupComment(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = feedbackfeed_examiner.GroupCommentEditView

    def test_edit_comment_draft_save(self):
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
                             feedback_set__group=group)

        mockresponse = self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': comment.id},
            requestkwargs={
                'data': {
                    'text': 'edited',
                    'submit-id-submit-save': True,
                }
            },
        )

        db_comment = group_models.GroupComment.objects.get(id=comment.id)
        self.assertEquals('edited', db_comment.text)

    def test_edit_comment_draft_save_continue_edit(self):
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
                             feedback_set__group=group)

        mockresponse = self.mock_http302_postrequest(
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
