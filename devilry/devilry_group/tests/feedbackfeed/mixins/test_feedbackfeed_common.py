from django.utils import timezone
from model_mommy import mommy

from django.utils import formats
from django_cradmin import cradmin_testhelpers

from devilry.devilry_group import models
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy


class TestFeedbackFeedHeaderMixin(cradmin_testhelpers.TestCaseMixin):

    def test_get_feedbackfeed_header(self):
        # check that header exists
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=mommy.make('devilry_group.FeedbackSet').group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-header'))

    def test_get_feedbackfeed_header_assignment_name(self):
        # check if the name of the assignment exists in view
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode__long_name='some_assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        assignment_name = mockresponse.selector.one('.devilry-group-feedbackfeed-header-assignment').alltext_normalized
        self.assertEqual(assignment_name, feedbackset.group.assignment.long_name)

    def test_get_feedbackfeed_header_subject_name(self):
        # check if the name of the subject exists in view
        group = mommy.make('core.AssignmentGroup', parentnode__parentnode__parentnode__long_name='some_subject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        subject_name = mockresponse.selector.one('.devilry-group-feedbackfeed-header-subject').alltext_normalized
        self.assertEqual(subject_name, group.assignment.period.subject.long_name)

    def test_get_feedbackfeed_header_period_name(self):
        # check if period name exists in view
        group = mommy.make('core.AssignmentGroup', parentnode__parentnode__long_name='some_period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        period_name = mockresponse.selector.one('.devilry-group-feedbackfeed-header-period').text_normalized
        self.assertEqual(period_name, group.assignment.period.long_name)

    def test_get_feedbackfeed_header_without_assignment_first_deadline(self):
        group = mommy.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))

    def test_get_feedbackfeed_header_with_assignment_first_deadline(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))

    def test_get_feedbackfeed_header_without_feedbackset_deadline_datetime(self):
        # tests that current-deadline-heading does not exist in view when feedbackset
        # has deadline_datetime set as none (no deadline) and assignment has no deadline.
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))

    def test_get_feedbackfeed_header_with_feedbackset_deadline_datetime(self):
        # tests that current-deadline-heading exists in view when feedbackset
        # has deadline_datetime set as a date.
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))

    def test_get_feedbackfeed_header_date_with_feedbackset_deadline_datetime(self):
        # tests that current-deadline-heading exists in view when feedbackset
        # has deadline_datetime set as a date.
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))
        self.assertEquals(
                mockresponse.selector.one('.devilry-group-feedbackfeed-current-deadline-datetime').alltext_normalized,
                formats.date_format(assignment.first_deadline, 'SHORT_DATETIME_FORMAT')
        )

    def test_get_feedbackfeed_header_date_with_multiple_feedbacksets(self):
        # test that the last deadline is shown as current deadline in view.
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   is_last_in_group=None)
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group=group,
                                 deadline_datetime=timezone.now(),
                                 feedbackset_type=models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))
        self.assertEquals(
                mockresponse.selector.one('.devilry-group-feedbackfeed-current-deadline-datetime').alltext_normalized,
                formats.date_format(feedbackset.deadline_datetime, 'SHORT_DATETIME_FORMAT')
        )

    def test_get_feedbackfeed_header_with_assignment_first_deadline_not_expired(self):
        # tests that current-deadline-expired does not exist in header in view and is
        # not expired with Assignment.first_deadline set
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-expired'))

    def test_get_feedbackfeed_header_with_assignment_first_deadline_expired(self):
        # tests that current-deadline-expired exist in header in view when only using Assignment.first_deadline
        # as expired.
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mommy.make('devilry_group.FeedbackSet', group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-expired'))

    def test_get_feedbackfeed_header_with_feedbackset_deadline_datetime_not_expired(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 deadline_datetime=timezone.now()+timezone.timedelta(days=1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-expired'))

    def test_get_feedbackfeed_header_with_feedbackset_deadline_datetime_expired(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-expired'))


class TestFeedbackFeedMixin(TestFeedbackFeedHeaderMixin):
    viewclass = None  # must be implemented in subclasses

    def test_get(self):
        group = mommy.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         group.assignment.get_path())

    def test_get_feedbackfeed_comment(self):
        comment = mommy.make('devilry_group.GroupComment',
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))

    def test_get_feedbackfeed_comment_student(self):
        comment = mommy.make('devilry_group.GroupComment',
                             user_role='student',
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-student'))

    def test_get_feedbackfeed_comment_examiner(self):
        comment = mommy.make('devilry_group.GroupComment',
                             user_role='examiner',
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-examiner'))

    def test_get_feedbackfeed_comment_admin(self):
        comment = mommy.make('devilry_group.GroupComment',
                             user_role='admin',
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-admin'))

    def test_get_feedbackfeed_comment_poster_fullname(self):
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent', user__fullname='Jane Doe'),)
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        self.assertTrue(comment.user.fullname, mockresponse.selector.one('.devilry-user-verbose-inline-fullname'))

    def test_get_feedbackfeed_comment_poster_shortname(self):
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent', user__fullname='Jane Doe'),)
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        self.assertTrue(comment.user.shortname, mockresponse.selector.one('.devilry-user-verbose-inline-shortname'))

    def test_get_feedbackfeed_comment_student_user_role(self):
        comment = mommy.make('devilry_group.GroupComment',
                             user_role='student',
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        role = mockresponse.selector.one('.comment-created-by-role-text').alltext_normalized
        self.assertEquals(role, '({})'.format(comment.user_role))

    def test_get_feedbackfeed_comment_examiner_user_role(self):
        comment = mommy.make('devilry_group.GroupComment',
                             user_role='examiner',
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        role = mockresponse.selector.one('.comment-created-by-role-text').alltext_normalized
        self.assertEquals(role, '({})'.format(comment.user_role))

    def test_get_feedbackfeed_comment_admin_user_role(self):
        comment = mommy.make('devilry_group.GroupComment',
                             user_role='admin',
                             visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        role = mockresponse.selector.one('.comment-created-by-role-text').alltext_normalized
        self.assertEquals(role, '({})'.format(comment.user_role))

    def test_get_feedbackfeed_event_without_any_deadlines_created(self):
        # Checks that when a feedbackset has been created and no first deadlines given, either on Assignment
        # or FeedbackSet, no 'created event' is rendered to template.
        group = mommy.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_get_feedbackfeed_event_without_any_deadlines_expired(self):
        # Checks that when a feedbackset has been created and no first deadlines given, either on Assignment
        # or FeedbackSet, no 'expired event' is rendered to template.
        group = mommy.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-expired'))

    def test_get_feedbackfeed_event_with_assignment_first_deadline_created(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_get_feedbackfeed_event_with_assignment_first_deadline_expired(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-expired'))

    def test_get_feedbackfeed_event_with_feedbackset_deadline_datetime_created(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 deadline_datetime=timezone.now()+timezone.timedelta(days=1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline'))
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-datetime'))

    def test_get_feedbackfeed_event_with_feedbackset_deadline_datetime_expired(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 deadline_datetime=timezone.now()-timezone.timedelta(days=1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-expired'))

    def test_get_feedbackfeed_event_without_feedbackset_deadline_datetime_created(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_futureperiod_start')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline'))
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-current-deadline-datetime'))

    def test_get_feedbackfeed_event_without_feedbackset_deadline_datetime_expired(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 deadline_datetime=timezone.now() + timezone.timedelta(days=10)
        )
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-event-message-deadline-expired'))

    def test_get_feedbackfeed_event_two_feedbacksets_deadlines_created(self):
        # test that two deadlines created events are rendered to view
        # using feedbackset deadline_datetime as deadlines(no assignment first_deadline)
        group = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   is_last_in_group=None,
                   created_datetime=timezone.now() - timezone.timedelta(days=2),
                   deadline_datetime=timezone.now() - timezone.timedelta(days=1))
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   # created_datetime=timezone.now() + timezone.timedelta(days=4),
                   feedbackset_type=models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT,
                   deadline_datetime=timezone.now() + timezone.timedelta(days=6))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        self.assertEqual(1, mockresponse.selector.count('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_get_feedbackfeed_event_two_feedbacksets_deadlines_expired(self):
        # test that two deadlines expired events are rendered to view
        # using feedbackset deadline_datetime as deadlines(no assignment first_deadline)
        group = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   is_last_in_group=None,
                   created_datetime=timezone.now() - timezone.timedelta(days=4),
                   deadline_datetime=timezone.now() - timezone.timedelta(days=3))
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   created_datetime=timezone.now() - timezone.timedelta(days=2),
                   deadline_datetime=timezone.now() - timezone.timedelta(days=1))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        expired = mockresponse.selector.list('.devilry-group-feedbackfeed-event-message-deadline-expired')
        # print mockresponse.selector.count('.devilry-group-feedbackfeed-event-message-deadline-expired')
        self.assertEqual(2, len(expired))

    def test_get_feedbackfeed_event_two_feedbacksets_deadlines_created_assignment_firstdeadline(self):
        # test that two deadline created events are rendered to view
        # using assignment first_deadline
        group = mommy.make('core.AssignmentGroup',
                           parentnode__first_deadline=timezone.now() + timezone.timedelta(days=3))
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   is_last_in_group=None)
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   feedbackset_type=models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT,
                   deadline_datetime=timezone.now() + timezone.timedelta(days=6))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        created = mockresponse.selector.list('.devilry-group-feedbackfeed-event-message-deadline-created')
        self.assertEqual(1, len(created))

    def test_get_feedbackfeed_event_two_feedbacksets_deadlines_expired_assignment_firstdeadline(self):
        # test that two deadline created events are rendered to view
        # using assignment first_deadline
        group = mommy.make('core.AssignmentGroup',
                           parentnode__first_deadline=timezone.now() - timezone.timedelta(days=8))
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   is_last_in_group=None)
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   created_datetime=timezone.now() - timezone.timedelta(days=6),
                   deadline_datetime=timezone.now() - timezone.timedelta(days=4))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group)
        expired = mockresponse.selector.list('.devilry-group-feedbackfeed-event-message-deadline-expired')
        self.assertEqual(2, len(expired))

    def test_post_302(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=feedbackset.group,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'asd',
                }
            })
        self.assertEquals(mockresponse.response.status_code, 302)
