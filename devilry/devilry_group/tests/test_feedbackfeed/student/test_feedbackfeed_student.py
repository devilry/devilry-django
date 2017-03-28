from datetime import timedelta

import mock
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy
from psycopg2.tests import unittest

from devilry.apps.core import models as core_models
from devilry.devilry_comment import models as comment_models
from devilry.devilry_compressionutil.models import CompressedArchiveMeta
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models as group_models
from devilry.devilry_group.tests.test_feedbackfeed.mixins import test_feedbackfeed_common
from devilry.devilry_group.views.student import feedbackfeed_student
from devilry.devilry_compressionutil import backend_registry
from devilry.devilry_compressionutil.backends import backend_mock


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
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=testgroup,
                              relatedexaminer__automatic_anonymous_id='AnonymousExaminer',
                              relatedexaminer__user__shortname='testexaminer')
        mommy.make('devilry_group.GroupComment',
                   user_role='examiner',
                   user=examiner.relatedexaminer.user,
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertFalse(mockresponse.selector.exists('.devilry-user-verbose-inline'))
        self.assertTrue(mockresponse.selector.exists('.devilry-core-examiner-anonymous-name'))
        self.assertEqual('AnonymousExaminer',
                         mockresponse.selector.one('.devilry-core-examiner-anonymous-name').alltext_normalized)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_download_not_visible_no_commentfiles_exists(self):
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-sidebar__title'))

    def test_get_feedbackfeed_download_visible_public_commentfiles_exist(self):
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        candidate = mommy.make('core.Candidate', assignment_group=testgroup)
        group_comment = mommy.make('devilry_group.GroupComment',
                                   user=candidate.relatedstudent.user,
                                   feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile', comment=group_comment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=testuser
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-sidebar'))

    def test_get_feedbackfeed_download_not_visible_private_commentfile_exist(self):
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        group_comment = mommy.make('devilry_group.GroupComment',
                                   feedback_set=testfeedbackset,
                                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE)
        mommy.make('devilry_comment.CommentFile', comment=group_comment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=testuser
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-sidebar__title'))

    def test_get_feedbackfeed_download_not_visible_part_of_grading_not_published(self):
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        group_comment = mommy.make('devilry_group.GroupComment',
                                   feedback_set=testfeedbackset,
                                   part_of_grading=True)
        mommy.make('devilry_comment.CommentFile', comment=group_comment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=testuser
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-sidebar__title'))

    def test_get_feedbackfeed_download_not_visible_comment_visible_to_examiners_and_admins(self):
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        group_comment = mommy.make('devilry_group.GroupComment',
                                   feedback_set=testfeedbackset,
                                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        mommy.make('devilry_comment.CommentFile', comment=group_comment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=testuser
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-sidebar__title'))

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
        self.assertEquals(1, group_models.FeedbackSet.objects.count())
        self.assertEqual(1, group_models.GroupComment.objects.count())
        self.assertIsNotNone(group_models.GroupComment.objects.all()[0].published_datetime)
        self.assertEqual('test', group_models.GroupComment.objects.all()[0].text)

    def test_post_feedbackset_post_comment_without_text(self):
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = mommy.make('core.Candidate', assignment_group=feedbackset.group)
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'student_add_comment': 'unused value',
                }
            })
        self.assertEquals(
            'A comment must have either text or a file attached, or both. An empty comment is not allowed.',
            mockresponse.selector.one('#error_1_id_text').alltext_normalized)
        self.assertEquals(0, group_models.GroupComment.objects.count())
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    #####
    # Tests making sure that event buttons are not rendered for
    # students(edit grade, new attempt, move deadlin etc.)
    ######

    def test_get_feedbackset_unpublished_header_buttons_not_rendered(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user,
        )
        self.assertFalse(
            mockresponse.selector.exists('.devilry-group-event__grade-move-deadline-button'))
        self.assertFalse(
            mockresponse.selector.exists('.devilry-group-event__grade-last-edit-button'))
        self.assertFalse(
            mockresponse.selector.exists('.devilry-group-event__grade-last-new-attempt-button'))
        self.assertNotIn('Move deadline', mockresponse.response.content)
        self.assertNotIn('Edit grade', mockresponse.response.content)
        self.assertNotIn('Give new attempt', mockresponse.response.content)

    def test_get_feedbackset_published_header_buttons_not_rendered(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=examiner.relatedexaminer.user,
        )
        self.assertFalse(
            mockresponse.selector.exists('.devilry-group-event__grade-move-deadline-button'))
        self.assertFalse(
            mockresponse.selector.exists('.devilry-group-event__grade-last-edit-button'))
        self.assertFalse(
            mockresponse.selector.exists('.devilry-group-event__grade-last-new-attempt-button'))
        self.assertNotIn('Move deadline', mockresponse.response.content)
        self.assertNotIn('Edit grade', mockresponse.response.content)
        self.assertNotIn('Give new attempt', mockresponse.response.content)


class TestFeedbackfeedGradeMappingStudent(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = feedbackfeed_student.StudentFeedbackFeedView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_event_grading_passed_failed_result_passed(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=1)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup
        )
        grade_result = mockresponse.selector.list('.devilry-core-grade')[0].alltext_normalized
        self.assertEquals(grade_result, 'passed')

    def test_get_event_grading_passed_failed_result_failed(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=0)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup
        )
        grade_result = mockresponse.selector.list('.devilry-core-grade')[0].alltext_normalized
        self.assertEquals(grade_result, 'failed')

    def test_get_event_grading_points_result_passed(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            students_can_see_points=True,
            points_to_grade_mapper=core_models.Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            passing_grade_min_points=50,
            max_points=100)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=75)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup
        )
        grade_result = mockresponse.selector.list('.devilry-core-grade')[0].alltext_normalized
        self.assertEquals(grade_result, '75/100 (passed)')

    def test_get_event_grading_points_result_failed(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            students_can_see_points=True,
            points_to_grade_mapper=core_models.Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            passing_grade_min_points=50,
            max_points=100)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=25)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup
        )
        grade_result = mockresponse.selector.list('.devilry-core-grade')[0].alltext_normalized
        self.assertEquals(grade_result, '25/100 (failed)')

    def test_get_event_grading_grade_mapper_failed(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            points_to_grade_mapper=core_models.Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
            passing_grade_min_points=10,
            max_points=35)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=5)
        point_to_grade_map = mommy.make('core.PointToGradeMap', assignment=testassignment)
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=5,
                   maximum_points=9, grade='F')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=10,
                   maximum_points=14, grade='E')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=15,
                   maximum_points=19, grade='D')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=20,
                   maximum_points=24, grade='C')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=25,
                   maximum_points=29, grade='B')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=30,
                   maximum_points=35, grade='A')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup
        )
        grade_result = mockresponse.selector.list('.devilry-core-grade')[0].alltext_normalized
        self.assertEquals(grade_result, 'F (failed)')

    def test_get_event_grading_grade_mapper_passed(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            points_to_grade_mapper=core_models.Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
            passing_grade_min_points=10,
            max_points=35)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=10)
        point_to_grade_map = mommy.make('core.PointToGradeMap', assignment=testassignment)
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=5,
                   maximum_points=9, grade='F')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=10,
                   maximum_points=14, grade='E')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=15,
                   maximum_points=19, grade='D')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=20,
                   maximum_points=24, grade='C')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=25,
                   maximum_points=29, grade='B')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=30,
                   maximum_points=35, grade='A')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup
        )
        grade_result = mockresponse.selector.list('.devilry-core-grade')[0].alltext_normalized
        self.assertEquals(grade_result, 'E (passed)')

    def test_get_event_grading_grade_mapper_failed_can_see_points(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            points_to_grade_mapper=core_models.Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
            students_can_see_points=True,
            passing_grade_min_points=10,
            max_points=35)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=5)
        point_to_grade_map = mommy.make('core.PointToGradeMap', assignment=testassignment)
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=5,
                   maximum_points=9, grade='F')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=10,
                   maximum_points=14, grade='E')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=15,
                   maximum_points=19, grade='D')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=20,
                   maximum_points=24, grade='C')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=25,
                   maximum_points=29, grade='B')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=30,
                   maximum_points=35, grade='A')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup
        )
        grade_result = mockresponse.selector.list('.devilry-core-grade')[0].alltext_normalized
        self.assertEquals(grade_result, 'F (failed - 5/35)')

    def test_get_event_grading_grade_mapper_passed_can_see_points(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            points_to_grade_mapper=core_models.Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
            students_can_see_points=True,
            passing_grade_min_points=10,
            max_points=35)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=10)
        point_to_grade_map = mommy.make('core.PointToGradeMap', assignment=testassignment)
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=5,
                   maximum_points=9, grade='F')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=10,
                   maximum_points=14, grade='E')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=15,
                   maximum_points=19, grade='D')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=20,
                   maximum_points=24, grade='C')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=25,
                   maximum_points=29, grade='B')
        mommy.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map, minimum_points=30,
                   maximum_points=35, grade='A')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup
        )
        grade_result = mockresponse.selector.list('.devilry-core-grade')[0].alltext_normalized
        self.assertEquals(grade_result, 'E (passed - 10/35)')




class TestFeedbackfeedFileUploadStudent(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = feedbackfeed_student.StudentFeedbackFeedView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        self.mock_registry = backend_registry.MockableRegistry.make_mockregistry(backend_mock.MockDevilryZipBackend)

    def test_add_comment_without_text_or_file(self):
        # Tests that error message pops up if trying to post a comment without either text or file.
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = mommy.make('core.Candidate', assignment_group=feedbackset.group)
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'student_add_comment': 'unused value'
                }
            })
        self.assertEquals(0, group_models.GroupComment.objects.count())
        self.assertEqual(
            'A comment must have either text or a file attached, or both. An empty comment is not allowed.',
            mockresponse.selector.one('#error_1_id_text').alltext_normalized)

    def test_upload_file_with_existing_archive_meta_for_feedbackset(self):
        # Tests that FeedbackFeedBaseViews _set_archive_meta_ready_for_delete function
        # marks the existing CompressedArchiveMeta for the FeedbackSet as ready for delete.
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = mommy.make('core.Candidate', assignment_group=testfeedbackset.group)
        testcomment = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))

        # Create existing archive meta
        # To make sure this does not fail(the model is cleaned and saved in the function)
        # self.mock_registry.add(backend_mock.MockDevilryZipBackend)
        test_archive_meta = mommy.make('devilry_compressionutil.CompressedArchiveMeta',
                                       content_object=testfeedbackset,
                                       backend_id=backend_mock.MockDevilryZipBackend.backend_id)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile.txt', content=b'Test content', content_type='text/txt')
            ],
            user=candidate.relatedstudent.user
        )

        with mock.patch('devilry.devilry_compressionutil.models.backend_registry.Registry._instance',
                        self.mock_registry):
            self.mock_http302_postrequest(
                cradmin_role=candidate.assignment_group,
                requestuser=candidate.relatedstudent.user,
                viewkwargs={'pk': testfeedbackset.group.id},
                requestkwargs={
                    'data': {
                        'text': '',
                        'student_add_comment': 'unused value',
                        'temporary_file_collection_id': temporary_filecollection.id
                    }
                })
        # we have to add a backend to the backendregistry.
        self.assertEquals(1, CompressedArchiveMeta.objects.filter(content_object_id=testfeedbackset.id).count())
        self.assertTrue(CompressedArchiveMeta.objects.get(id=test_archive_meta.id).delete)

    def test_upload_single_file(self):
        # Test that a CommentFile is created on upload.
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = mommy.make('core.Candidate', assignment_group=feedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfile(
            user=candidate.relatedstudent.user)
        self.mock_http302_postrequest(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'student_add_comment': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, group_models.GroupComment.objects.count())
        self.assertEquals(1, comment_models.CommentFile.objects.count())

    def test_upload_single_file_content(self):
        # Test the content of a CommentFile after upload.
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = mommy.make('core.Candidate', assignment_group=feedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile.txt', content=b'Test content', content_type='text/txt')
            ],
            user=candidate.relatedstudent.user
        )
        self.mock_http302_postrequest(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'student_add_comment': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(1, comment_models.CommentFile.objects.count())
        comment_file = comment_models.CommentFile.objects.all()[0]
        self.assertEqual('testfile.txt', comment_file.filename)
        self.assertEqual('Test content', comment_file.file.file.read())
        self.assertEqual(len('Test content'), comment_file.filesize)
        self.assertEqual('text/txt', comment_file.mimetype)

    def test_upload_multiple_files(self):
        # Test the content of a CommentFile after upload.
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = mommy.make('core.Candidate', assignment_group=feedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
                SimpleUploadedFile(name='testfile3.txt', content=b'Test content3', content_type='text/txt')
            ],
            user=candidate.relatedstudent.user
        )
        self.mock_http302_postrequest(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'student_add_comment': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(3, comment_models.CommentFile.objects.count())

    def test_upload_multiple_files_contents(self):
        # Test the content of a CommentFile after upload.
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = mommy.make('core.Candidate', assignment_group=feedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
                SimpleUploadedFile(name='testfile3.txt', content=b'Test content3', content_type='text/txt')
            ],
            user=candidate.relatedstudent.user
        )
        self.mock_http302_postrequest(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': '',
                    'student_add_comment': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(3, comment_models.CommentFile.objects.count())
        comment_file1 = comment_models.CommentFile.objects.get(filename='testfile1.txt')
        comment_file2 = comment_models.CommentFile.objects.get(filename='testfile2.txt')
        comment_file3 = comment_models.CommentFile.objects.get(filename='testfile3.txt')

        # Check content of testfile 1.
        self.assertEqual('Test content1', comment_file1.file.file.read())
        self.assertEqual(len('Test content1'), comment_file1.filesize)
        self.assertEqual('text/txt', comment_file1.mimetype)

        # Check content of testfile 2.
        self.assertEqual('Test content2', comment_file2.file.file.read())
        self.assertEqual(len('Test content2'), comment_file2.filesize)
        self.assertEqual('text/txt', comment_file2.mimetype)

        # Check content of testfile 3.
        self.assertEqual('Test content3', comment_file3.file.file.read())
        self.assertEqual(len('Test content3'), comment_file3.filesize)
        self.assertEqual('text/txt', comment_file3.mimetype)

    def test_upload_files_with_comment_text(self):
        # Test the content of a CommentFile after upload.
        feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        candidate = mommy.make('core.Candidate', assignment_group=feedbackset.group)
        temporary_filecollection = group_mommy.temporary_file_collection_with_tempfiles(
            file_list=[
                SimpleUploadedFile(name='testfile1.txt', content=b'Test content1', content_type='text/txt'),
                SimpleUploadedFile(name='testfile2.txt', content=b'Test content2', content_type='text/txt'),
            ],
            user=candidate.relatedstudent.user
        )
        self.mock_http302_postrequest(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'Test comment',
                    'student_add_comment': 'unused value',
                    'temporary_file_collection_id': temporary_filecollection.id
                }
            })
        self.assertEquals(2, comment_models.CommentFile.objects.count())
        self.assertEquals(1, group_models.GroupComment.objects.count())
        self.assertEquals('Test comment', group_models.GroupComment.objects.all()[0].text)

    def test_comment_only_with_text(self):
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

        self.assertEquals(1, group_models.GroupComment.objects.count())
        self.assertEqual('test', group_models.GroupComment.objects.all()[0].text)
        self.assertEqual(0, comment_models.CommentFile.objects.count())


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
        mommy.make('core.Candidate', assignment_group=testgroup, _quantity=50)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mommy.make('core.Examiner', assignmentgroup=testgroup, _quantity=50)
        candidate = mommy.make('core.Candidate', assignment_group=testgroup)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role='student',
                   feedback_set=testfeedbackset,
                   _quantity=20)
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=testfeedbackset,
                   _quantity=20)
        mock_cradmininstance = mock.MagicMock()
        mock_cradmininstance.get_devilryrole_for_requestuser.return_value = 'student'
        with self.assertNumQueries(18):
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
        mommy.make('core.Candidate', assignment_group=testgroup, _quantity=50)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mommy.make('core.Examiner', assignmentgroup=testgroup, _quantity=50)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             feedback_set=testfeedbackset)
        comment2 = mommy.make('devilry_group.GroupComment',
                              user=examiner.relatedexaminer.user,
                              user_role='examiner',
                              feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile',
                   filename='test.py',
                   comment=comment,
                   _quantity=20)
        mommy.make('devilry_comment.CommentFile',
                   filename='test2.py',
                   comment=comment2,
                   _quantity=20)
        with self.assertNumQueries(21):
            self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                               requestuser=candidate.relatedstudent.user)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())
