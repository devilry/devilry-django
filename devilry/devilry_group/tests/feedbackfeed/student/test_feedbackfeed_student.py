import mock
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy
from psycopg2.tests import unittest

from devilry.apps.core import models as core_models
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models as group_models
from devilry.devilry_group.tests.feedbackfeed.mixins import test_feedbackfeed_common
from devilry.devilry_group.views.student import feedbackfeed_student
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestFeedbackfeedStudent(TestCase, test_feedbackfeed_common.TestFeedbackFeedMixin):
    """
    General testing of what gets rendered to student view.
    """
    viewclass = feedbackfeed_student.StudentFeedbackFeedView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get(self):
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized,
                          candidate.assignment_group.assignment.get_path())
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_anonymous_examiner_semi(self):
        testassignment = mommy.make('core.Assignment',
                                    anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        candidate = mommy.make('core.Examiner',
                               assignmentgroup=testgroup,
                               relatedexaminer__automatic_anonymous_id='AnonymousExaminer',
                               relatedexaminer__user__shortname='testexaminer')
        mommy.make('devilry_group.GroupComment',
                   user_role='examiner',
                   user=candidate.relatedexaminer.user,
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertFalse(mockresponse.selector.exists('.devilry-user-verbose-inline'))
        self.assertTrue(mockresponse.selector.exists('.devilry-core-examiner-anonymous-name'))
        self.assertEqual('AnonymousExaminer',
                         mockresponse.selector.one('.devilry-core-examiner-anonymous-name').alltext_normalized)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_anonymous_examiner_fully(self):
        testassignment = mommy.make('core.Assignment',
                                    anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        candidate = mommy.make('core.Examiner',
                               assignmentgroup=testgroup,
                               relatedexaminer__automatic_anonymous_id='AnonymousExaminer',
                               relatedexaminer__user__shortname='testexaminer')
        mommy.make('devilry_group.GroupComment',
                   user_role='examiner',
                   user=candidate.relatedexaminer.user,
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertFalse(mockresponse.selector.exists('.devilry-user-verbose-inline'))
        self.assertTrue(mockresponse.selector.exists('.devilry-core-examiner-anonymous-name'))
        self.assertEqual('AnonymousExaminer',
                         mockresponse.selector.one('.devilry-core-examiner-anonymous-name').alltext_normalized)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_student_cannot_see_feedback_or_discuss_in_header(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-feedback-button'))
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-discuss-button'))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_student_add_comment_to_feedbackset_without_deadline(self):
        testgroup = mommy.make('core.AssignmentGroup')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group=testgroup)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        comment = mommy.make('devilry_group.GroupComment',
                             user_role='student',
                             user=candidate.relatedstudent.user,
                             published_datetime=timezone.now(),
                             feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        self.assertTrue(mockresponse.selector.one('.devilry-group-feedbackfeed-comment-student'))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackset_student_comment_after_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             published_datetime=timezone.now() + timezone.timedelta(days=1),
                             feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertTrue(mockresponse.selector.exists('.after-deadline-badge'))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackset_student_comment_after_deadline_with_new_feedbackset(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        feedbackset1 = group_mommy.feedbackset_first_attempt_published(group=testgroup)
        feedbackset2 = group_mommy.feedbackset_new_attempt_unpublished(
                group=testgroup,
                deadline_datetime=timezone.now() - timezone.timedelta(days=1))
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
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertTrue(mockresponse.selector.exists('.after-deadline-badge'))
        self.assertEquals(2, group_models.FeedbackSet.objects.count())

    def test_get_feedbackset_comment_student_before_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                             published_datetime=timezone.now(),
                             feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertFalse(mockresponse.selector.exists('.after-deadline-badge'))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_student_can_see_other_student_comments(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        janedoe = mommy.make('core.Candidate',
                             assignment_group=testgroup,
                             relatedstudent=mommy.make('core.RelatedStudent'))
        johndoe = mommy.make('core.Candidate',
                             assignment_group=testgroup,
                             relatedstudent=mommy.make('core.RelatedStudent', user__fullname='John Doe'))
        mommy.make('devilry_group.GroupComment',
                   user=johndoe.relatedstudent.user,
                   user_role='student',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=timezone.now(),
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=janedoe.assignment_group,
                                                          requestuser=janedoe.relatedstudent.user)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(johndoe.relatedstudent.user.fullname, name)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_student_can_see_other_student_comments_after_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        janedoe = mommy.make('core.Candidate',
                             assignment_group=testgroup,
                             relatedstudent=mommy.make('core.RelatedStudent'),)
        johndoe = mommy.make('core.Candidate',
                             assignment_group=testgroup,
                             relatedstudent=mommy.make('core.RelatedStudent', user__fullname='John Doe'))
        mommy.make('devilry_group.GroupComment',
                   user=johndoe.relatedstudent.user,
                   user_role='student',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=timezone.now(),
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=janedoe.assignment_group,
                                                          requestuser=janedoe.relatedstudent.user)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertTrue(mockresponse.selector.one('.after-deadline-badge'))
        self.assertEquals(johndoe.relatedstudent.user.fullname, name)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_student_can_see_examiner_visibility_visible_to_everyone(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='John Doe'))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=timezone.now(),
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(examiner.relatedexaminer.user.fullname, name)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_student_can_see_examiner_visibility_visible_to_everyone_after_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=candidate.assignment_group,
                              relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='John Doe'),)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=timezone.now(),
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(examiner.relatedexaminer.user.fullname, name)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_student_can_not_see_examiner_comment_visibility_visible_to_examiner_and_admins(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent__user=requestuser)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer__user=mommy.make(settings.AUTH_USER_MODEL))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   published_datetime=timezone.now() - timezone.timedelta(days=1),
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_student_can_not_see_admin_comment_visibility_visible_to_examiner_and_admins(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        admin = mommy.make('devilry_account.User', shortname='subjectadmin')
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', parentnode__admins=[admin])
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent__user=requestuser)
        mommy.make('devilry_group.GroupComment',
                   user=admin,
                   user_role='admin',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-admin'))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_student_cannot_see_comment_visibility_private(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='John Doe'),)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   published_datetime=timezone.now(),
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_post_feedbackset_comment_with_text(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
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
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_post_feedbackset_comment_with_text_published_datetime_is_set(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
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
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    @unittest.skip('Ignored - must be updated for issue ')
    def test_post_feedbackset_post_comment_without_text(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        student = mommy.make('core.Candidate', assignment_group=feedbackset.group,
                             # NOTE: The line below can be removed when relatedstudent field is migrated to null=False
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
        self.assertEquals(1, group_models.FeedbackSet.objects.count())


class TestFeedbackPublishingStudent(TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    Test what gets rendered and not rendered to student view of elements
    that belongs to publishing of feedbacksets.
    """
    viewclass = feedbackfeed_student.StudentFeedbackFeedView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_feedbackfeed_event_delivery_passed(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       max_points=10,
                                       passing_grade_min_points=5)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=7)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertTrue(mockresponse.selector.exists('.devilry-core-grade-passed'))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_event_delivery_failed(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       max_points=10,
                                       passing_grade_min_points=5)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=3)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertTrue(mockresponse.selector.exists('.devilry-core-grade-failed'))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_student_can_not_see_comments_part_of_grading_before_publish_first_attempt(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent__user=requestuser)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer__user=mommy.make(settings.AUTH_USER_MODEL))
        mommy.make('devilry_group.GroupComment',
                   text='asd',
                   part_of_grading=True,
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_student_can_not_see_comments_part_of_grading_before_publish_new_attempt(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       max_points=10,
                                       passing_grade_min_points=5)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        feedbackset_last = group_mommy.feedbackset_new_attempt_unpublished(
                group=testgroup,
                deadline_datetime=timezone.now()+timezone.timedelta(days=1))
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
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
        self.assertEquals(2, group_models.FeedbackSet.objects.count())

    def test_get_student_can_see_comments_part_of_grading_after_publish_first_attempt(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='John Doe'),)
        mommy.make('devilry_group.GroupComment',
                   text='asd',
                   part_of_grading=True,
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=testfeedbackset)
        mommy.make('devilry_group.GroupComment',
                   text='asd',
                   part_of_grading=True,
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        feedback_comments = mockresponse.selector.list('.devilry-group-feedbackfeed-comment')
        self.assertEquals(2, len(feedback_comments))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_student_can_see_comments_part_of_grading_before_publish_new_attempt(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       max_points=10,
                                       passing_grade_min_points=5)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        feedbackset_last = group_mommy.feedbackset_new_attempt_published(
                group=testgroup,
                deadline_datetime=timezone.now()+timezone.timedelta(days=1))
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent=mommy.make('core.RelatedStudent'))
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='John Doe'))
        mommy.make('devilry_group.GroupComment',
                   text='asd',
                   part_of_grading=True,
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=feedbackset_last)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))
        self.assertEquals(2, group_models.FeedbackSet.objects.count())

    def test_get_num_queries(self):
        testgroup = mommy.make('core.AssignmentGroup')
        candidate = mommy.make('core.Candidate', assignment_group=testgroup)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role='student',
                   feedback_set=testfeedbackset)
        mock_cradmininstance = mock.MagicMock()
        mock_cradmininstance.get_devilryrole_for_requestuser.return_value = 'student'
        with self.assertNumQueries(10):
            self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                               requestuser=candidate.relatedstudent.user,
                                               cradmin_instance=mock_cradmininstance)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_num_queries_with_commentfiles(self):
        """
        NOTE: (works as it should)
        Checking that no more queries are executed even though the
        :func:`devilry.devilry_group.feedbackfeed_builder.FeedbackFeedTimelineBuilder.__get_feedbackset_queryset`
        duplicates comment_file query.
        """
        testgroup = mommy.make('core.AssignmentGroup')
        candidate = mommy.make('core.Candidate', assignment_group=testgroup)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             feedback_set=testfeedbackset)
        comment2 = mommy.make('devilry_group.GroupComment',
                              user=candidate.relatedstudent.user,
                              user_role='student',
                              feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile',
                   filename='test.py',
                   comment=comment,
                   _quantity=100)
        mommy.make('devilry_comment.CommentFile',
                   filename='test2.py',
                   comment=comment2,
                   _quantity=100)
        with self.assertNumQueries(10):
            self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                               requestuser=candidate.relatedstudent.user)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())
