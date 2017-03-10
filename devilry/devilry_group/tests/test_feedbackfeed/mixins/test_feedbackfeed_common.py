import unittest

import mock

from django.utils import formats
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models
from devilry.devilry_group import models as group_models


class TestFeedbackFeedHeaderMixin(cradmin_testhelpers.TestCaseMixin):
    """
    Tests the header of the feedbackfeed and elements that should be rendered inside it.
    """
    def test_get_header(self):
        # tests that that header exists in header
        group = mommy.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-header'))

    def test_get_header_assignment_name(self):
        # tests that the name of the assignment exists in header
        group = mommy.make('core.AssignmentGroup', parentnode__long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        assignment_name = mockresponse.selector.one('.devilry-group-feedbackfeed-header-assignment').alltext_normalized
        self.assertEqual(assignment_name, 'Test Assignment')

    def test_get_header_subject_name(self):
        # tests that the name of the subject exists in header
        group = mommy.make('core.AssignmentGroup', parentnode__parentnode__parentnode__long_name='some_subject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        subject_name = mockresponse.selector.one('.devilry-group-feedbackfeed-header-subject').alltext_normalized
        self.assertEqual(subject_name, group.assignment.period.subject.long_name)

    def test_get_header_period_name(self):
        # tests that period name exists in header
        group = mommy.make('core.AssignmentGroup', parentnode__parentnode__long_name='some_period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        period_name = mockresponse.selector.one('.devilry-group-feedbackfeed-header-period').text_normalized
        self.assertEqual(period_name, group.assignment.period.long_name)

    @unittest.skip("Depends on FeedbackSets deadline_datetime being None. Will be removed")
    def test_get_header_without_deadline(self):
        # tests that current deadline does not exist in header when Assignment and FeedbackSet has no deadline set.
        testgroup = mommy.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))

    def test_get_header_with_assignment_first_deadline_only(self):
        # tests that current deadline exists in header when Assignment.first_deadline is set.
        # Only Assignment.first_deadline is set (not FeedbackSet.deadline_datetime)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))
        self.assertEquals(
                mockresponse.selector.one('.devilry-group-feedbackfeed-current-deadline-datetime').alltext_normalized,
                formats.date_format(testassignment.first_deadline, 'SHORT_DATETIME_FORMAT')
        )

    def test_get_header_with_feedbackset_deadline_datetime_only(self):
        # tests that current deadline exists in header when FeedbackSet.deadline_datetime is set.
        # Only FeedbackSet.deadline_datetime is set (not Assignment.first_deadline)
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = mommy.make('devilry_group.FeedbackSet', group=testgroup, deadline_datetime=timezone.now())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))
        self.assertEquals(
                mockresponse.selector.one('.devilry-group-feedbackfeed-current-deadline-datetime').alltext_normalized,
                formats.date_format(testfeedbackset.deadline_datetime, 'SHORT_DATETIME_FORMAT')
        )

    def test_get_header_current_deadline(self):
        # tests that when both Assignment.first_deadline and FeedbackSet.deadline_datetime is set and
        # FeedbackSet.feedbackset_type is FIRST_ATTEMPT, the deadline of the Assignment should be rendered
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))
        self.assertEquals(
                mockresponse.selector.one('.devilry-group-feedbackfeed-current-deadline-datetime').alltext_normalized,
                formats.date_format(testassignment.first_deadline, 'SHORT_DATETIME_FORMAT')
        )

    def test_get_header_date_with_multiple_feedbacksets(self):
        # tests that if there are multiple FeedbackSets', the deadline of the last FeedbackSet should be shown.
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(
                group=testgroup
        )
        testfeedbackset = group_mommy.feedbackset_new_attempt_unpublished(
                group=testgroup,
                deadline_datetime=timezone.now() + timezone.timedelta(days=10))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testfeedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))
        self.assertEquals(
                mockresponse.selector.one('.devilry-group-feedbackfeed-current-deadline-datetime').alltext_normalized,
                formats.date_format(testfeedbackset.deadline_datetime, 'SHORT_DATETIME_FORMAT')
        )

    def test_get_header_with_assignment_first_deadline_not_expired(self):
        # tests that current-deadline-expired does not exist in header when Assignment.first_deadline is set
        # with a deadline in the future
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-expired'))
        self.assertEquals(
                mockresponse.selector.one('.devilry-group-feedbackfeed-current-deadline-datetime').alltext_normalized,
                formats.date_format(testassignment.first_deadline, 'SHORT_DATETIME_FORMAT')
        )

    def test_get_header_with_assignment_first_deadline_expired(self):
        # tests that current-deadline-expired exist in header when only Assignment.first_deadline is set
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-expired'))
        self.assertEquals(
                mockresponse.selector.one('.devilry-group-feedbackfeed-current-deadline-expired').alltext_normalized,
                'Expired - {}'.format(formats.date_format(testassignment.first_deadline, 'SHORT_DATETIME_FORMAT'))
        )

    def test_get_header_with_feedbackset_deadline_datetime_not_expired(self):
        # tests that current-deadline-expired does not exist in header when only FeedbackSet.deadline_datetime is set
        # with a deadline in the future.
        testfeedbackset = mommy.make('devilry_group.FeedbackSet',
                                     deadline_datetime=timezone.now()+timezone.timedelta(days=10))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testfeedbackset.group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-expired'))
        self.assertEquals(
                mockresponse.selector.one('.devilry-group-feedbackfeed-current-deadline-datetime').alltext_normalized,
                formats.date_format(testfeedbackset.deadline_datetime, 'SHORT_DATETIME_FORMAT')
        )

    def test_get_header_with_feedbackset_deadline_datetime_expired(self):
        # tests that current-deadline-expired exists in header when only FeedbackSet.deadline_datetime is set
        # and the deadline in the past.
        testfeedbackset = mommy.make('devilry_group.FeedbackSet',
                                     deadline_datetime=timezone.now() - timezone.timedelta(days=10))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testfeedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-expired'))
        self.assertEquals(
                mockresponse.selector.one('.devilry-group-feedbackfeed-current-deadline-expired').alltext_normalized,
                'Expired - {}'.format(formats.date_format(testfeedbackset.deadline_datetime, 'SHORT_DATETIME_FORMAT'))
        )


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


class TestFeedbackFeedGroupCommentMixin(cradmin_testhelpers.TestCaseMixin):
    """
    Tests the rendering of GroupComment in a feedbackfeed.
    """
    def test_get_comment_student(self):
        # test that student comment-style is rendered.
        group = mommy.make('core.AssignmentGroup')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group=group)
        mommy.make('devilry_group.GroupComment',
                   user_role='student',
                   user=candidate.relatedstudent.user,
                   feedback_set=group.feedbackset_set.first())
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group,
                                                          cradmin_instance=_get_mock_cradmin_instance())
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-student'))

    def test_get_comment_examiner(self):
        # test that examiner comment-style is rendered.
        group = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group)
        mommy.make('devilry_group.GroupComment',
                   user_role='examiner',
                   user=examiner.relatedexaminer.user,
                   feedback_set=group.feedbackset_set.first(),
                   visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group,
                                                          cradmin_instance=_get_mock_cradmin_instance())
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-examiner'))

    def test_get_comment_admin(self):
        # test that student comment-style is rendered.
        group = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=group.feedbackset_set.first(),
                   user_role='admin',
                   visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-admin'))

    def test_get_comment_poster_fullname(self):
        # tests that the comment-posters fullname is rendered
        group = mommy.make('core.AssignmentGroup')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent', user__fullname='Jane Doe'),
                               assignment_group=group)
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             feedback_set=group.feedbackset_set.first(),
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group,
                                                          cradmin_instance=_get_mock_cradmin_instance())
        self.assertTrue(comment.user.fullname, mockresponse.selector.one('.devilry-user-verbose-inline-fullname'))

    def test_get_comment_poster_shortname(self):
        # tests that the comment-posters shortname is rendered
        group = mommy.make('core.AssignmentGroup')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent', user__fullname='Jane Doe'),
                               assignment_group=group)
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             feedback_set=group.feedbackset_set.first(),
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group,
                                                          cradmin_instance=_get_mock_cradmin_instance())
        self.assertTrue(comment.user.shortname, mockresponse.selector.one('.devilry-user-verbose-inline-shortname'))

    def test_get_comment_student_user_role(self):
        # tests that the role of a student comment is 'student'
        group = mommy.make('core.AssignmentGroup')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group=group)
        comment = mommy.make('devilry_group.GroupComment',
                             user_role='student',
                             user=candidate.relatedstudent.user,
                             feedback_set=group.feedbackset_set.first(),
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group,
                                                          cradmin_instance=_get_mock_cradmin_instance())
        self.assertEquals('(student)', mockresponse.selector.one('.comment-created-by-role-text').alltext_normalized)

    def test_get_comment_examiner_user_role(self):
        # tests that the role of an examiner comment is 'examiner'
        group = mommy.make('core.AssignmentGroup')
        comment = mommy.make('devilry_group.GroupComment',
                             feedback_set=group.feedbackset_set.first(),
                             user_role='examiner',
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group,
                                                          cradmin_instance=_get_mock_cradmin_instance())
        self.assertEquals('(examiner)', mockresponse.selector.one('.comment-created-by-role-text').alltext_normalized)

    def test_get_comment_admin_user_role(self):
        # tests that the role of an admin comment is 'admin'
        group = mommy.make('core.AssignmentGroup')
        comment = mommy.make('devilry_group.GroupComment',
                             feedback_set=group.feedbackset_set.first(),
                             user_role='admin',
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertEquals('(admin)', mockresponse.selector.one('.comment-created-by-role-text').alltext_normalized)


class TestFeedbackFeedMixin(TestFeedbackFeedHeaderMixin, TestFeedbackFeedGroupCommentMixin):
    """
    Mixin testclass for all feedbackfeed tests.

    Add tests for functionality and ui that all feedbackfeed views share.
    """
    viewclass = None  # must be implemented in subclass

    def test_get(self):
        group = mommy.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         group.assignment.get_path())

    def test_get_event_without_any_deadlines_created(self):
        # tests that when a feedbackset has been created and no first deadlines given, either on Assignment
        # or FeedbackSet, no 'created event' is rendered
        group = mommy.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_get_event_without_any_deadlines_expired(self):
        # tests that when a feedbackset has been created and no first deadlines given, either on Assignment
        # or FeedbackSet, no 'expired event' is rendered
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-expired'))

    def test_get_event_with_assignment_first_deadline_created(self):
        # tests that when the first deadline is given, either on Assignment or FeedbackSet, no 'created event' is
        # rendered
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_get_event_with_assignment_first_deadline_expired(self):
        # tests that an 'deadline expired'-event occurs when Assignment.first_deadline expires.
        # NOTE: FeedbackSet.deadline_datetime is not set.
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-expired'))

    def test_get_event_with_feedbackset_deadline_datetime_expired(self):
        # tests that an 'deadline expired'-event occurs when FeedbackSet.deadline_datetime expires.
        # NOTE: Assignment.first_deadline is not set.
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 deadline_datetime=timezone.now()-timezone.timedelta(days=1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-expired'))

    def test_get_event_without_feedbackset_deadline_datetime_expired(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_unpublished(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-expired'))

    def test_get_event_two_feedbacksets_deadlines_created(self):
        # test that two deadlines created events are rendered to view
        # using feedbackset deadline_datetime as deadlines(no assignment first_deadline)
        group = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   feedbackset_type=models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT,
                   deadline_datetime=timezone.now() - timezone.timedelta(days=1))
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   # created_datetime=timezone.now() + timezone.timedelta(days=4),
                   feedbackset_type=models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT,
                   deadline_datetime=timezone.now() + timezone.timedelta(days=6))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertEqual(2, mockresponse.selector.count('.devilry-group-feedbackfeed-event-message-deadline-created'))

    # def test_get_event_two_feedbacksets_deadlines_expired(self):
    #     # test that two deadlines expired events are rendered to view
    #     testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
    #     group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
    #     group_mommy.feedbackset_first_attempt_published(group=group)
    #     group_mommy.feedbackset_new_attempt_published(
    #         group=group,
    #         deadline_datetime=timezone.now() - timezone.timedelta(days=1))
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
    #     expired = mockresponse.selector.list('.devilry-group-feedbackfeed-event-message-deadline-expired')
    #     self.assertEqual(2, len(expired))

    def test_get_event_two_feedbacksets_deadlines_created_assignment_firstdeadline(self):
        # test that two deadline created events are rendered to view
        # using assignment first_deadline
        group = mommy.make('core.AssignmentGroup',
                           parentnode__first_deadline=timezone.now() + timezone.timedelta(days=3))
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   feedbackset_type=models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT,
                   deadline_datetime=timezone.now() + timezone.timedelta(days=6))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        created = mockresponse.selector.list('.devilry-group-feedbackfeed-event-message-deadline-created')
        self.assertEqual(1, len(created))

    def test_get_event_two_feedbacksets_deadlines_expired_assignment_firstdeadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       first_deadline=timezone.now() - timezone.timedelta(days=4))
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        group_mommy.feedbackset_new_attempt_unpublished(
                group=testgroup,
                deadline_datetime=timezone.now() - timezone.timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        expired = mockresponse.selector.list('.devilry-group-feedbackfeed-event-message-deadline-expired')
        self.assertEqual(2, len(expired))
        self.assertEquals(2, group_models.FeedbackSet.objects.count())

    def test_post_302(self):
        group = mommy.make('core.AssignmentGroup')
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=group,
            viewkwargs={'pk': group.id},
            requestkwargs={
                'data': {
                    'passed': 'Passed',
                    'text': 'asd',
                }
            })
