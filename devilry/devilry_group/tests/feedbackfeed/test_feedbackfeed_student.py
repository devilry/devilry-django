from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models as group_models
from devilry.devilry_group.tests.feedbackfeed.mixins import test_feedbackfeed_common
from devilry.devilry_group.views import feedbackfeed_student


class TestFeedbackfeedStudent(TestCase, test_feedbackfeed_common.TestFeedbackFeedMixin):
    """
    General testing of what gets rendered to student view.
    """
    viewclass = feedbackfeed_student.StudentFeedbackFeedView

    def test_get(self):
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized,
                          candidate.assignment_group.assignment.get_path())

    def test_get_feedbackfeed_student_cannot_see_feedback_or_discuss_in_header(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = mommy.make('core.Candidate',
                               assignment_group=group,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-feedback-button'))
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-discuss-button'))

    def test_get_feedbackfeed_student_add_comment_to_feedbackset_without_deadline(self):
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'))
        comment = mommy.make('devilry_group.GroupComment',
                             user_role='student',
                             published_datetime=timezone.now(),
                             feedback_set__group=candidate.assignment_group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertTrue(mockresponse.selector.one('.devilry-group-feedbackfeed-comment-student'))

    def test_get_feedbackset_student_comment_after_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             published_datetime=timezone.now() + timezone.timedelta(days=1),
                             feedback_set__group=candidate.assignment_group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertTrue(mockresponse.selector.exists('.after-deadline-badge'))

    def test_get_feedbackset_student_comment_after_deadline_with_new_feedbackset(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = mommy.make('core.Candidate',
                               assignment_group=group,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  group=group,
                                  is_last_in_group=False)
        feedbackset2 = mommy.make('devilry_group.FeedbackSet',
                                  group=group,
                                  deadline_datetime=timezone.now()+timezone.timedelta(days=1))
        mommy.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role='student',
                   published_datetime=timezone.now(),
                   feedback_set=feedbackset1)
        mommy.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role='student',
                   published_datetime=timezone.now(),
                   feedback_set=feedbackset2)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertTrue(mockresponse.selector.exists('.after-deadline-badge'))

    def test_get_feedbackset_comment_student_before_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                             published_datetime=timezone.now(),
                             feedback_set__group=candidate.assignment_group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertFalse(mockresponse.selector.exists('.after-deadline-badge'))

    def test_get_feedbackfeed_student_can_see_other_student_comments(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        janedoe = mommy.make('core.Candidate',
                             assignment_group__parentnode=assignment,
                             relatedstudent=mommy.make('core.RelatedStudent'))
        johndoe = mommy.make('core.Candidate',
                             assignment_group=janedoe.assignment_group,
                             relatedstudent=mommy.make('core.RelatedStudent', user__fullname='John Doe'))
        mommy.make('devilry_group.GroupComment',
                   user=johndoe.relatedstudent.user,
                   user_role='student',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=timezone.now(),
                   feedback_set__group=johndoe.assignment_group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=janedoe.assignment_group,
                                                          requestuser=janedoe.relatedstudent.user)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(johndoe.relatedstudent.user.fullname, name)

    def test_get_feedbackfeed_student_can_see_other_student_comments_after_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        janedoe = mommy.make('core.Candidate',
                             assignment_group__parentnode=assignment,
                             relatedstudent=mommy.make('core.RelatedStudent'),)
        johndoe = mommy.make('core.Candidate',
                             assignment_group=janedoe.assignment_group,
                             relatedstudent=mommy.make('core.RelatedStudent', user__fullname='John Doe'))
        mommy.make('devilry_group.GroupComment',
                   user=johndoe.relatedstudent.user,
                   user_role='student',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=timezone.now(),
                   feedback_set__group=johndoe.assignment_group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=janedoe.assignment_group,
                                                          requestuser=janedoe.relatedstudent.user)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertTrue(mockresponse.selector.one('.after-deadline-badge'))
        self.assertEquals(johndoe.relatedstudent.user.fullname, name)

    def test_get_feedbackfeed_student_can_see_examiner_visibility_visible_to_everyone(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        candidate = mommy.make('core.Candidate',
                               assignment_group__assignment=assignment,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=candidate.assignment_group,
                              relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='John Doe'))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=timezone.now(),
                   feedback_set__group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(examiner.relatedexaminer.user.fullname, name)

    def test_get_feedbackfeed_student_can_see_examiner_visibility_visible_to_everyone_after_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        candidate = mommy.make('core.Candidate',
                               assignment_group__assignment=assignment,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=candidate.assignment_group,
                              relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='John Doe'),)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=timezone.now(),
                   feedback_set__group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(examiner.relatedexaminer.user.fullname, name)

    def test_get_feedbackfeed_student_can_not_see_examiner_comment_visibility_visible_to_examiner_and_admins(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = mommy.make('core.Candidate',
                               assignment_group=group,
                               relatedstudent__user=requestuser)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer__user=mommy.make(settings.AUTH_USER_MODEL))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   published_datetime=timezone.now() - timezone.timedelta(days=1),
                   feedback_set__group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))

    def test_get_feedbackfeed_student_can_not_see_admin_comment_visibility_visible_to_examiner_and_admins(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        admin = mommy.make('devilry_account.User', shortname='subjectadmin')
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', parentnode__admins=[admin])
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)

        candidate = mommy.make('core.Candidate',
                               assignment_group=group,
                               relatedstudent__user=requestuser)

        mommy.make('devilry_group.GroupComment',
                   user=admin,
                   user_role='admin',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   feedback_set__group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-admin'))

    def test_get_student_cannot_see_comment_visibility_private(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        candidate = mommy.make('core.Candidate',
                               assignment_group__assignment=assignment,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        examiner = mommy.make('core.Examiner', assignmentgroup=candidate.assignment_group,
                              relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='John Doe'),)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   published_datetime=timezone.now(),
                   feedback_set__group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))

    def test_post_feedbackset_comment_with_text(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        candidate = mommy.make('core.Candidate', assignment_group=feedbackset.group,
                               # NOTE: The line below can be removed when relatedstudent field is migrated to null=False
                               relatedstudent=mommy.make('core.RelatedStudent'))
        self.mock_http302_postrequest(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'test',
                    'student_add_comment': 'unused value',
                }
            })
        self.assertEquals(1, len(group_models.GroupComment.objects.all()))

    def test_post_feedbackset_comment_with_text_published_datetime_is_set(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        candidate = mommy.make('core.Candidate', assignment_group=feedbackset.group,
                               # NOTE: The line below can be removed when relatedstudent field is migrated to null=False
                               relatedstudent=mommy.make('core.RelatedStudent'))
        self.mock_http302_postrequest(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'test',
                    'student_add_comment': 'unused value',
                }
            })
        self.assertIsNotNone(group_models.GroupComment.objects.all()[0].published_datetime)

    def test_post_feedbackset_post_comment_without_text(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        student = mommy.make('core.Candidate', assignment_group=feedbackset.group,
                             # NOTE: The line blow can be removed when relatedstudent field is migrated to null=False
                             relatedstudent=mommy.make('core.RelatedStudent'))
        self.mock_http302_postrequest(
            cradmin_role=student.assignment_group,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'student_add_comment': 'unused value',
                }
            })
        self.assertEquals(0, len(group_models.GroupComment.objects.all()))


class TestFeedbackPublishingStudent(TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    Test what gets rendered and not rendered to student view of elements
    that belongs to publishing of feedbacksets.
    """
    viewclass = feedbackfeed_student.StudentFeedbackFeedView

    def test_get_feedbackfeed_event_delivery_passed(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode__max_points=10,
                                 group__parentnode__passing_grade_min_points=5,
                                 grading_published_datetime=timezone.now(),
                                 deadline_datetime=timezone.now(),
                                 grading_points=7)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-core-grade-passed'))

    def test_get_feedbackfeed_event_delivery_failed(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode__max_points=10,
                                 group__parentnode__passing_grade_min_points=5,
                                 grading_published_datetime=timezone.now(),
                                 grading_points=3)

        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-core-grade-failed'))

    def test_get_student_can_not_see_comments_part_of_grading_before_publish_first_attempt(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_middle')
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished(group__parentnode=assignment)
        candidate = mommy.make('core.Candidate',
                               assignment_group=feedbackset.group,
                               relatedstudent__user=requestuser)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer__user=mommy.make(settings.AUTH_USER_MODEL))
        mommy.make('devilry_group.GroupComment',
                   text='asd',
                   part_of_grading=True,
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))

    def test_get_student_can_not_see_comments_part_of_grading_before_publish_new_attempt(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup',
                           parentnode=assignment)
        group_mommy.feedbackset_first_attempt_published(
                group=group,
                is_last_in_group=None)
        feedbackset_last = group_mommy.feedbackset_new_attempt_unpublished(
                group=group,
                deadline_datetime=timezone.now()+timezone.timedelta(days=1))
        candidate = mommy.make('core.Candidate',
                               assignment_group=group,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='John Doe'),)
        mommy.make('devilry_group.GroupComment',
                   text='asd',
                   part_of_grading=True,
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset_last)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))

    def test_get_student_can_see_comments_part_of_grading_after_publish_first_attempt(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = group_mommy.feedbackset_first_attempt_published(group__parentnode=assignment)
        candidate = mommy.make('core.Candidate',
                               assignment_group=feedbackset.group,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='John Doe'),)
        mommy.make('devilry_group.GroupComment',
                   text='asd',
                   part_of_grading=True,
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset)
        mommy.make('devilry_group.GroupComment',
                   text='asd',
                   part_of_grading=True,
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        feedback_comments = mockresponse.selector.list('.devilry-group-feedbackfeed-comment')
        self.assertEquals(2, len(feedback_comments))