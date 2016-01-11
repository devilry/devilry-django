from django.test import TestCase
from django.utils import timezone, formats
from model_mommy import mommy

from devilry.devilry_group.tests import test_feedbackfeed_common
from devilry.devilry_group.views import feedbackfeed_student
from devilry.devilry_group.models import GroupComment


class TestFeedbackfeedStudent(TestCase, test_feedbackfeed_common.TestFeedbackFeedMixin):
    viewclass = feedbackfeed_student.StudentFeedbackFeedView

    def test_get(self):
        student = mommy.make('core.Candidate')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=student.assignment_group,
                                                          requestuser=student.student)
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized,
                          student.assignment_group.assignment.get_path())

    def test_get_feedbackfeed_student_add_comment_to_feedbackset_without_deadline(self):
        student = mommy.make('core.Candidate')
        comment = mommy.make('devilry_group.GroupComment',
                             user_role='student',
                             published_datetime=timezone.now(),
                             feedback_set__group=student.assignment_group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group,
                                                          requestuser=student)
        self.assertTrue(mockresponse.selector.one('.devilry-group-feedbackfeed-comment-student'))

    def test_get_feedbackset_student_comment_after_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        candidate = mommy.make('core.Candidate', assignment_group__parentnode=assignment)
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.student,
                             user_role='student',
                             published_datetime=timezone.now() + timezone.timedelta(days=1),
                             feedback_set__group=candidate.assignment_group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        self.assertTrue(mockresponse.selector.exists('.after-deadline-badge'))

    def test_get_feedbackset_student_comment_after_deadline_with_new_feedbackset(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = mommy.make('core.Candidate', assignment_group=group)
        feedbackset1 = mommy.make('devilry_group.FeedbackSet', group=group, is_last_in_group=False)
        feedbackset2 = mommy.make('devilry_group.FeedbackSet', group=group, deadline_datetime=timezone.now()+timezone.timedelta(days=1))
        mommy.make('devilry_group.GroupComment',
                             user=candidate.student,
                             user_role='student',
                             published_datetime=timezone.now(),
                             feedback_set=feedbackset1)
        mommy.make('devilry_group.GroupComment',
                             user=candidate.student,
                             user_role='student',
                             published_datetime=timezone.now(),
                             feedback_set=feedbackset2)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertTrue(mockresponse.selector.exists('.after-deadline-badge'))

    def test_get_feedbackset_comment_student_before_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        candidate = mommy.make('core.Candidate', assignment_group__parentnode=assignment)
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.student,
                             user_role='student',
                             visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                             published_datetime=timezone.now(),
                             feedback_set__group=candidate.assignment_group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        self.assertFalse(mockresponse.selector.exists('.after-deadline-badge'))

    def test_get_feedbackfeed_student_can_see_other_student_comments(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        janedoe = mommy.make('core.Candidate', assignment_group__parentnode=assignment)
        johndoe = mommy.make('core.Candidate', assignment_group=janedoe.assignment_group, student__fullname='John Doe')
        mommy.make('devilry_group.GroupComment',
                   user=johndoe.student,
                   user_role='student',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=timezone.now(),
                   feedback_set__group=johndoe.assignment_group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=janedoe.assignment_group)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(johndoe.student.fullname, name)

    def test_get_feedbackfeed_student_can_see_other_student_comments_after_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        janedoe = mommy.make('core.Candidate', assignment_group__parentnode=assignment)
        johndoe = mommy.make('core.Candidate', assignment_group=janedoe.assignment_group, student__fullname='John Doe')
        mommy.make('devilry_group.GroupComment',
                   user=johndoe.student,
                   user_role='student',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=timezone.now(),
                   feedback_set__group=johndoe.assignment_group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=janedoe.assignment_group)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertTrue(mockresponse.selector.one('.after-deadline-badge'))
        self.assertEquals(johndoe.student.fullname, name)

    # def test_get_feedbackfeed_student_can_see_admin_comment(self):
    #     assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
    #     group = mommy.make('core.AssignmentGroup', parentnode=assignment)
    #     examiner = mommy.make('core.Examiner', assignmentgroup=group, user__fullname='Examiner')
    #     candidate = mommy.make('core.Candidate', assignment_group=group, student__fullname='Student')
    #     feedbackset = mommy.make('devilry_group.FeedbackSet', group=group)
    #     comment = mommy.make('devilry_group.GroupComment',
    #                          user=examiner.user,
    #                          user_role='examiner',
    #                          instant_publish=True,
    #                          visible_for_students=True,
    #                          published_datetime=timezone.now(),
    #                          feedback_set=feedbackset)
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
    #                                                       requestuser=candidate.student)
    #     self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-admin'))

    def test_get_feedbackfeed_student_can_see_examiner_visibility_visible_to_everyone(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        student = mommy.make('core.Candidate', assignment_group__assignment=assignment)
        examiner = mommy.make('core.Examiner', assignmentgroup=student.assignment_group, user__fullname='John Doe')
        mommy.make('devilry_group.GroupComment',
                   user=examiner.user,
                   user_role='examiner',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=timezone.now(),
                   feedback_set__group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=student.assignment_group)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(examiner.user.fullname, name)

    def test_get_feedbackfeed_student_can_see_examiner_visibility_visible_to_everyone_after_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        student = mommy.make('core.Candidate', assignment_group__assignment=assignment)
        examiner = mommy.make('core.Examiner', assignmentgroup=student.assignment_group, user__fullname='John Doe')
        mommy.make('devilry_group.GroupComment',
                   user=examiner.user,
                   user_role='examiner',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=timezone.now(),
                   feedback_set__group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=student.assignment_group)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(examiner.user.fullname, name)

    def test_get_feedbackfeed_student_can_not_see_examiner_comment_visibility_visible_to_examiner_and_admins(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        student = mommy.make('core.Candidate', assignment_group__assignment=assignment)
        examiner = mommy.make('core.Examiner', assignmentgroup=student.assignment_group, user__fullname='John Doe')
        mommy.make('devilry_group.GroupComment',
                   user=examiner.user,
                   user_role='examiner',
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   published_datetime=timezone.now() - timezone.timedelta(days=1),
                   feedback_set__group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=student.assignment_group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-comment-created-by-role'))

    def test_post_feedbackset_comment_with_text(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        student = mommy.make('core.Candidate', assignment_group=feedbackset.group)
        self.mock_http302_postrequest(
            cradmin_role=student.assignment_group,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'test',
                }
            })
        self.assertEquals(1, len(GroupComment.objects.all()))

    def test_post_feedbackset_post_comment_without_text(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        student = mommy.make('core.Candidate', assignment_group=feedbackset.group)
        self.mock_http302_postrequest(
            cradmin_role=student.assignment_group,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                }
            })
        self.assertEquals(0, len(GroupComment.objects.all()))
