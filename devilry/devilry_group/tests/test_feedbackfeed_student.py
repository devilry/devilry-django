from django.test import TestCase, RequestFactory
from django.utils import timezone
import htmls
import mock
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

    def test_get_feedbackset_student_comment_after_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        candidate = mommy.make('core.Candidate', assignment_group__parentnode=assignment)
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.student,
                             user_role='student',
                             # instant_publish=True,
                             # visible_for_students=True,
                             visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                             published_datetime=timezone.now() + timezone.timedelta(days=1),
                             feedback_set__group=candidate.assignment_group,
                             feedback_set__deadline_datetime=timezone.now())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group,
                                                          requestuser=comment.user)
        self.assertTrue(mockresponse.selector.exists('.after-deadline-badge'))

    def test_get_feedbackset_comment_student_before_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        candidate = mommy.make('core.Candidate', assignment_group__parentnode=assignment)
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.student,
                             user_role='student',
                             # instant_publish=True,
                             # visible_for_students=True,
                             visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                             published_datetime=timezone.now() - timezone.timedelta(days=1),
                             feedback_set__group=candidate.assignment_group,
                             feedback_set__deadline_datetime=timezone.now())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group,
                                                          requestuser=comment.user)
        self.assertFalse(mockresponse.selector.exists('.after-deadline-badge'))

    def test_get_feedbackfeed_student_can_see_other_student_comments(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        janedoe = mommy.make('core.Candidate', assignment_group=group, student__fullname='Jane Doe')
        johndoe = mommy.make('core.Candidate', assignment_group=group, student__fullname='John Doe')
        comment = mommy.make('devilry_group.GroupComment',
                             user=johndoe.student,
                             user_role='student',
                             # instant_publish=True,
                             # visible_for_students=True,
                             visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                             published_datetime=timezone.now() - timezone.timedelta(days=1),
                             feedback_set__group=group,
                             feedback_set__deadline_datetime=timezone.now())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=janedoe.assignment_group,
                                                          requestuser=janedoe.student)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
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

    # def test_get_feedbackfeed_student_can_see_examiner_comment_visible_to_students_true(self):
    #     janedoe = UserBuilder2(fullname='Jane Doe').user
    #     examiner = UserBuilder2(fullname='John Doe').user
    #     time = timezone.now()
    #     feedbackset_builder = FeedbackSetBuilder.make(
    #         group__assignment__first_deadline=time,
    #         deadline_datetime = time
    #     )
    #     feedbackset_builder.add_groupcomment(
    #         user=examiner,
    #         user_role='examiner',
    #         instant_publish=True,
    #         visible_for_students=True,
    #         text="hello world",
    #         grading_published_datetime=timezone.now()
    #     )
    #     selector, request = self._mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
    #                                                              requestuser=janedoe,
    #                                                              group=janedoe)
    #     self.assertTrue(selector.exists('.devilry-group-feedbackfeed-comment-examiner'))
    #
    # def test_get_feedbackfeed_student_can_not_see_examiner_comment_visible_to_students_false(self):
    #     janedoe = UserBuilder2(fullname='Jane Doe').user
    #     examiner = UserBuilder2(fullname='John Doe').user
    #     time = timezone.now()
    #     feedbackset_builder = FeedbackSetBuilder.make(
    #         group__assignment__first_deadline=time,
    #         deadline_datetime = time
    #     )
    #     feedbackset_builder.add_groupcomment(
    #         user=examiner,
    #         user_role='examiner',
    #         instant_publish=True,
    #         visible_for_students=False,
    #         text="hello world",
    #         grading_published_datetime=timezone.now()
    #     )
    #     selector, request = self._mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
    #                                                              requestuser=janedoe,
    #                                                              group=janedoe)
    #     self.assertFalse(selector.exists('.devilry-group-feedbackfeed-comment-examiner'))
    #
    # def test_post(self):
    #     janedoe = UserBuilder2(fullname='Jane Doe').user
    #     assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
    #     assignment_group = mommy.make('core.AssignmentGroup')
    #     response, request = self._mock_postrequest(role=assignment_group, requestuser=janedoe, group=janedoe)
    #
    #     self.assertEquals(response.status_code, 200)

    # def test_post_feedbackset_post_comment(self):
    #     feedbackset = mommy.make('devilry_group.FeedbackSet',
    #                              group__parentnode__max_points=10,
    #                              group__parentnode__passing_grade_min_points=5)
    #     mockresponse = self.mock_http302_postrequest(
    #         cradmin_role=feedbackset.group,
    #         viewkwargs={'pk': feedbackset.group.id},
    #         requestkwargs={
    #             'data': {
    #                 'text': 'test',
    #             }
    #         })
    #
    #     comment = GroupComment.objects.filter(feedback_set__id=feedbackset.id)
    #     self.assertEquals(1, len(comment))
    #
    # def test_post_feedbackset_post_comment_no_text(self):
    #     feedbackset = mommy.make('devilry_group.FeedbackSet',
    #                              group__parentnode__max_points=10,
    #                              group__parentnode__passing_grade_min_points=5)
    #     mockresponse = self.mock_http302_postrequest(
    #         cradmin_role=feedbackset.group,
    #         viewkwargs={'pk': feedbackset.group.id},
    #         requestkwargs={
    #             'data': {
    #                 'text': '',
    #             }
    #         })
    #     comments = GroupComment.objects.all()
    #     self.assertEquals(0, len(comments))