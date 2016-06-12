from django.test import TestCase
from model_mommy import mommy

from django_cradmin import cradmin_testhelpers
from devilry.devilry_group.views import feedbackfeed_examiner
from devilry.devilry_group import models as group_models


class TestFeedbackFeedDeleteComment(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = feedbackfeed_examiner.GroupCommentDeleteView

    def test_delete_comment_draft(self):
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
            viewkwargs={'pk': comment.id},
        )

        self.assertEquals(0, len(group_models.GroupComment.objects.all()))
