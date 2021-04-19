import unittest

import mock
from django.conf import settings
from django.contrib import messages

from django.utils import formats
from django.utils import timezone
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.devilry_group import devilry_group_baker_factories as group_baker
from devilry.devilry_group import models
from devilry.devilry_group import models as group_models


class MixinTestFeedbackFeedHeader(cradmin_testhelpers.TestCaseMixin):
    """
    Tests the header of the feedbackfeed and elements that should be rendered inside it.
    """
    def test_get_header(self):
        # tests that that header exists in header
        group = baker.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-header'))

    def test_get_header_assignment_name(self):
        # tests that the name of the assignment exists in header
        group = baker.make('core.AssignmentGroup', parentnode__long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        assignment_name = mockresponse.selector.one('.devilry-group-feedbackfeed-header-assignment').alltext_normalized
        self.assertEqual(assignment_name, 'Test Assignment')

    def test_get_header_subject_name(self):
        # tests that the name of the subject exists in header
        group = baker.make('core.AssignmentGroup', parentnode__parentnode__parentnode__long_name='some_subject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        subject_name = mockresponse.selector.one('.devilry-group-feedbackfeed-header-subject').alltext_normalized
        self.assertEqual(subject_name, group.assignment.period.subject.long_name)

    def test_get_header_period_name(self):
        # tests that period name exists in header
        group = baker.make('core.AssignmentGroup', parentnode__parentnode__long_name='some_period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        period_name = mockresponse.selector.one('.devilry-group-feedbackfeed-header-period').text_normalized
        self.assertEqual(period_name, group.assignment.period.long_name)


def _get_mock_cradmin_instance():
    """
    If the subclass that implements a mixin view is :class:`devilry.devilry_group.views.AdminFeedbackFeedView`
    we need a admin devilry role for the cradmininstance, so we just mock a returnvalue for the
    :func:`~devilry.devilry_group.cradmin_instances.AdminCrInstance.get_devilry_role_for_requestuser`.

    Returns:
         Mocked cradmininstance.
    """
    mockrequest = mock.MagicMock()
    mockrequest.cradmin_instance.get_devilryrole_for_requestuser.return_value = 'subjectadmin'
    return mockrequest.cradmin_instance


class MixinTestFeedbackFeedGroupComment(cradmin_testhelpers.TestCaseMixin):
    """
    Tests the rendering of GroupComment in a feedbackfeed.
    """
    def test_get_feedbackfeed_candidate_user_deleted(self):
        testassignment = baker.make('core.Assignment')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        baker.make('devilry_group.GroupComment',
                   user_role='student',
                   user=None,
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertEqual('USER DELETED',
                         mockresponse.selector.one('.devilry-group-comment-user-deleted').alltext_normalized)

    def test_get_feedbackfeed_examiner_user_deleted(self):
        testassignment = baker.make('core.Assignment')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        baker.make('devilry_group.GroupComment',
                   user_role='examiner',
                   user=None,
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertEqual('USER DELETED',
                         mockresponse.selector.one('.devilry-group-comment-user-deleted').alltext_normalized)

    def test_get_feedbackfeed_admin_user_deleted(self):
        testassignment = baker.make('core.Assignment')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        baker.make('devilry_group.GroupComment',
                   user_role='admin',
                   user=None,
                   feedback_set=testfeedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertEqual('USER DELETED',
                         mockresponse.selector.one('.devilry-group-comment-user-deleted').alltext_normalized)

    def test_get_comment_student(self):
        # test that student comment-style is rendered.
        group = baker.make('core.AssignmentGroup')
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'),
                               assignment_group=group)
        baker.make('devilry_group.GroupComment',
                   user_role='student',
                   user=candidate.relatedstudent.user,
                   feedback_set=group.feedbackset_set.first())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group,
                                                          cradmin_instance=_get_mock_cradmin_instance())
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-student'))

    def test_get_comment_examiner(self):
        # test that examiner comment-style is rendered.
        group = baker.make('core.AssignmentGroup')
        examiner = baker.make('core.Examiner',
                              assignmentgroup=group)
        baker.make('devilry_group.GroupComment',
                   user_role='examiner',
                   user=examiner.relatedexaminer.user,
                   feedback_set=group.feedbackset_set.first(),
                   visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group,
                                                          cradmin_instance=_get_mock_cradmin_instance())
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-examiner'))

    def test_get_comment_admin(self):
        # test that student comment-style is rendered.
        group = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set=group.feedbackset_set.first(),
                   user_role='admin',
                   visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-admin'))

    def test_get_comment_poster_fullname(self):
        # tests that the comment-posters fullname is rendered
        group = baker.make('core.AssignmentGroup')
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent', user__fullname='Jane Doe'),
                               assignment_group=group)
        comment = baker.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             feedback_set=group.feedbackset_set.first(),
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group,
                                                          cradmin_instance=_get_mock_cradmin_instance())
        self.assertTrue(comment.user.fullname, mockresponse.selector.one('.devilry-user-verbose-inline-fullname'))

    def test_get_comment_poster_shortname(self):
        # tests that the comment-posters shortname is rendered
        group = baker.make('core.AssignmentGroup')
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent', user__fullname='Jane Doe'),
                               assignment_group=group)
        comment = baker.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             feedback_set=group.feedbackset_set.first(),
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group,
                                                          cradmin_instance=_get_mock_cradmin_instance())
        self.assertTrue(comment.user.shortname, mockresponse.selector.one('.devilry-user-verbose-inline-shortname'))

    def test_get_comment_student_user_role(self):
        # tests that the role of a student comment is 'student'
        group = baker.make('core.AssignmentGroup')
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'),
                               assignment_group=group)
        comment = baker.make('devilry_group.GroupComment',
                             user_role='student',
                             user=candidate.relatedstudent.user,
                             feedback_set=group.feedbackset_set.first(),
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group,
                                                          cradmin_instance=_get_mock_cradmin_instance())
        self.assertEqual('(student)', mockresponse.selector.one('.comment-created-by-role-text').alltext_normalized)

    def test_get_comment_examiner_user_role(self):
        # tests that the role of an examiner comment is 'examiner'
        group = baker.make('core.AssignmentGroup')
        comment = baker.make('devilry_group.GroupComment',
                             feedback_set=group.feedbackset_set.first(),
                             user_role='examiner',
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group,
                                                          cradmin_instance=_get_mock_cradmin_instance())
        self.assertEqual('(examiner)', mockresponse.selector.one('.comment-created-by-role-text').alltext_normalized)

    def test_get_comment_admin_user_role(self):
        # tests that the role of an admin comment is 'admin'
        group = baker.make('core.AssignmentGroup')
        comment = baker.make('devilry_group.GroupComment',
                             feedback_set=group.feedbackset_set.first(),
                             user_role='admin',
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertEqual('(admin)', mockresponse.selector.one('.comment-created-by-role-text').alltext_normalized)


class MixinTestFeedbackFeed(MixinTestFeedbackFeedHeader, MixinTestFeedbackFeedGroupComment):
    """
    Mixin testclass for all feedbackfeed tests.

    Add tests for functionality and ui that all feedbackfeed views share.
    """
    viewclass = None  # must be implemented in subclass

    def test_get(self):
        group = baker.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         group.assignment.get_path())

    def test_semester_expired_comment_form_not_rendered(self):
        # Test comment/upload form is not rendered if the semester has expired.
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group__parentnode__parentnode=baker.make_recipe('devilry.apps.core.period_old'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=test_feedbackset.group,
            requestuser=testuser
        )
        self.assertFalse(mockresponse.selector.exists('.cradmin-legacy-form-wrapper'))

    def test_semester_expired_comment_form_not_rendered_message_box(self):
        # Test comment/upload form is not rendered if the semester has expired.
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group__parentnode__parentnode=baker.make_recipe('devilry.apps.core.period_old'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=test_feedbackset.group,
            requestuser=testuser
        )
        self.assertFalse(mockresponse.selector.exists('.cradmin-legacy-form-wrapper'))
        self.assertTrue(mockresponse.selector.exists('.devilry-feedbackfeed-form-disabled'))
        self.assertEqual(mockresponse.selector.one('.devilry-feedbackfeed-form-disabled').alltext_normalized,
                         'File uploads and comments disabled This assignment is on an inactive semester. '
                         'File upload and commenting is disabled.')

    def test_semester_expired_post_django_message(self):
        # Test comment/upload form post django message if the semester has expired.
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group__parentnode__parentnode=baker.make_recipe('devilry.apps.core.period_old'))
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=test_feedbackset.group,
            requestuser=testuser,
            viewkwargs={'pk': test_feedbackset.group.id},
            messagesmock=messagesmock,
            requestkwargs={
                'data': {
                    'text': 'test',
                    'student_add_comment': 'unused value',
                }
            })
        messagesmock.add.assert_called_once_with(
            messages.WARNING, 'This assignment is on an inactive semester. File upload and commenting is disabled.', '')
        self.assertEqual(group_models.GroupComment.objects.count(), 0)

    def test_get_event_without_any_deadlines_expired(self):
        # tests that when a feedbackset has been created and no first deadlines given, either on Assignment
        # or FeedbackSet, no 'expired event' is rendered
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_unpublished(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-expired'))

    def test_get_event_with_assignment_first_deadline_expired(self):
        # tests that an 'deadline expired'-event occurs when Assignment.first_deadline expires.
        # NOTE: FeedbackSet.deadline_datetime is not set.
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message__deadline-expired'))

    def test_get_event_with_feedbackset_deadline_datetime_expired(self):
        # tests that an 'deadline expired'-event occurs when FeedbackSet.deadline_datetime expires.
        # NOTE: Assignment.first_deadline is not set.
        feedbackset = baker.make('devilry_group.FeedbackSet',
                                 deadline_datetime=timezone.now()-timezone.timedelta(days=1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message__deadline-expired'))

    def test_get_event_without_feedbackset_deadline_datetime_expired(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_unpublished(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message__deadline-expired'))

    def test_get_event_two_feedbacksets_deadlines_expired_assignment_firstdeadline(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       first_deadline=timezone.now() - timezone.timedelta(days=4))
        testgroup = baker.make('core.AssignmentGroup', parentnode=assignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup)
        group_baker.feedbackset_new_attempt_unpublished(
                group=testgroup,
                deadline_datetime=timezone.now() - timezone.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        expired = mockresponse.selector.list('.devilry-group-feedbackfeed-event-message__deadline-expired')
        self.assertEqual(2, len(expired))
        self.assertEqual(2, group_models.FeedbackSet.objects.count())

    def test_get_feedbackset_header(self):
        testgroup = baker.make('core.AssignmentGroup')
        group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
        )
        self.assertTrue(
            mockresponse.selector.one('.devilry-group-feedbackfeed-feed__feedbackset-wrapper--header-first-attempt'))

    def test_get_feedbackset_header_title(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        with self.settings(DATETIME_FORMAT='l j F, Y, H:i', USE_L10N=False):
            mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
            )
        self.assertEqual(mockresponse.selector.one('.header-title').alltext_normalized,
                          'Deadline: Saturday 15 January, 2000, 23:59')

    def test_get_feedbackset_header_attempt(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
        )
        self.assertEqual(mockresponse.selector.one('.header-attempt-number').alltext_normalized,
                          'Attempt 1')

    def test_get_feedbackset_header_grading_info_waiting_for_feedback(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
        )
        self.assertEqual(mockresponse.selector.one('.header-grading-info').alltext_normalized, 'waiting for feedback')

    def test_get_feedbackset_header_grading_info_waiting_for_deliveries_for_feedback(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_middle')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
        )
        self.assertEqual(mockresponse.selector.one('.header-grading-info').alltext_normalized,
                          'waiting for deliveries')

    def test_get_feedbackset_header_two_attempts(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup)
        group_baker.feedbackset_new_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
        )
        self.assertEqual(mockresponse.selector.list('.header-attempt-number')[0].alltext_normalized,
                          'Attempt 1')
        self.assertEqual(mockresponse.selector.list('.header-attempt-number')[1].alltext_normalized,
                          'Attempt 2')

    def test_get_feedbackset_deadline_history_username_rendered(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        testuser = baker.make(settings.AUTH_USER_MODEL, shortname='test@example.com', fullname='Test User')
        baker.make('devilry_group.FeedbackSetDeadlineHistory', feedback_set=testgroup.cached_data.first_feedbackset,
                   changed_by=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup
        )
        self.assertEqual(
            mockresponse.selector.one('.devilry-group-feedbackfeed-event-message__user_display_name')
                .alltext_normalized,
            'Test User(test@example.com)'
        )

    def test_get_feedbackset_grading_updated_one_event_rendered(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_published(group=testgroup, grading_points=1)
        testuser = baker.make(settings.AUTH_USER_MODEL, shortname='test@example.com', fullname='Test User')
        baker.make('devilry_group.FeedbackSetGradingUpdateHistory', feedback_set=test_feedbackset, old_grading_points=1,
                   updated_by=testuser)

        # We add an unpublished new attempt, because the feedback view for examiners requires that the last feedbackset
        # is not published.
        group_baker.feedbackset_new_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup
        )
        self.assertEqual(mockresponse.selector.count('.devilry-group-event__grading_updated'), 1)

    def test_get_feedbackset_grading_updated_multiple_events_rendered(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        test_feedbackset = group_baker.feedbackset_first_attempt_published(group=testgroup, grading_points=1)
        testuser = baker.make(settings.AUTH_USER_MODEL, shortname='test@example.com', fullname='Test User')
        baker.make('devilry_group.FeedbackSetGradingUpdateHistory', feedback_set=test_feedbackset, old_grading_points=1,
                   updated_by=testuser)
        baker.make('devilry_group.FeedbackSetGradingUpdateHistory', feedback_set=test_feedbackset, old_grading_points=0,
                   updated_by=testuser)
        baker.make('devilry_group.FeedbackSetGradingUpdateHistory', feedback_set=test_feedbackset, old_grading_points=1,
                   updated_by=testuser)
        baker.make('devilry_group.FeedbackSetGradingUpdateHistory', feedback_set=test_feedbackset, old_grading_points=0,
                   updated_by=testuser)

        # We add an unpublished new attempt, because the feedback view for examiners requires that the last feedbackset
        # is not published.
        group_baker.feedbackset_new_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup
        )
        self.assertEqual(mockresponse.selector.count('.devilry-group-event__grading_updated'), 4)
