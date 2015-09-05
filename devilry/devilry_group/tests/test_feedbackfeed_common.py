from datetime import datetime
from django.template import defaultfilters
from django.test import RequestFactory
from django.utils import timezone
import htmls
import mock

from devilry.project.develop.testhelpers.corebuilder import UserBuilder2, AssignmentGroupBuilder, FeedbackSetBuilder, \
    GroupCommentBuilder
from devilry.project.develop.testhelpers.datebuilder import DateTimeBuilder


class TestFeedbackFeedMixin(object):
    viewclass = None  # must be implemented in subclasses

    def __mock_request(self, method, role, requestuser, group,
                       messagesmock=None):
        request = getattr(RequestFactory(), method)('/')
        request.user = requestuser
        request.cradmin_role = role
        request.cradmin_app = mock.MagicMock()
        request.cradmin_instance = mock.MagicMock()
        request.session = mock.MagicMock()
        if messagesmock:
            request._messages = messagesmock
        else:
            request._messages = mock.MagicMock()
        response = self.viewclass.as_view()(request, pk=group.pk)
        return response, request

    def __mock_http200_getrequest_htmls(self, role, requestuser, group):
        response, request = self.__mock_request(method='get',
                                                role=role,
                                                requestuser=requestuser,
                                                group=group)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        return selector, request

    def __mock_postrequest(self, role, requestuser, group, messagesmock=None):
        return self.__mock_request(method='post',
                                   role=role,
                                   requestuser=requestuser,
                                   group=group,
                                   messagesmock=messagesmock)

    def test_get(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        group_builder = AssignmentGroupBuilder.make()
        selector, request = self.__mock_http200_getrequest_htmls(role=group_builder.get_object(),
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertEqual(selector.one('title').alltext_normalized,
                         group_builder.group.assignment.get_path())

    def test_get_feedbackset(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make()
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-feed'))

    def test_get_feedbackset_header(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make()
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-header'))

    def test_get_feedbackset_header_assignment_name(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make()
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        assignment_name = selector.one('.devilry-group-feedbackfeed-header-assignment').text_normalized
        self.assertEqual(assignment_name, feedbackset_builder.get_object().group.assignment.short_name)

    def test_get_feedbackset_header_subject_name(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make()
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        subject_name = selector.one('.devilry-group-feedbackfeed-header-subject').text_normalized
        self.assertEqual(subject_name, feedbackset_builder.get_object().group.assignment.period.subject.long_name)

    def test_get_feedbackset_header_period_name(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make()
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        period_name = selector.one('.devilry-group-feedbackfeed-header-period').text_normalized
        self.assertEqual(period_name, feedbackset_builder.get_object().group.assignment.period.long_name)

    def test_get_feedbackset_header_without_first_deadline(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        group_builder = AssignmentGroupBuilder.make(assignment__first_deadline=None)
        selector, request = self.__mock_http200_getrequest_htmls(role=group_builder.get_object(),
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertFalse(selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))

    def test_get_feedbackset_header_with_first_deadline(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        group_builder = AssignmentGroupBuilder.make(assignment__first_deadline=timezone.now())
        selector, request = self.__mock_http200_getrequest_htmls(role=group_builder.get_object(),
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))

    def test_get_feedbackset_header_without_deadline_datetime(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        groupcomment_builder = GroupCommentBuilder.make(feedback_set__deadline_datetime=None)

        selector, request = self.__mock_http200_getrequest_htmls(role=groupcomment_builder.get_object().feedback_set.group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertFalse(selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))

    def test_get_feedbackset_header_with_current_deadline_not_expired(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        groupcomment_builder = GroupCommentBuilder.make(feedback_set__deadline_datetime=DateTimeBuilder.now().plus(days=1))

        selector, request = self.__mock_http200_getrequest_htmls(role=groupcomment_builder.get_object().feedback_set.group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-current-deadline'))

    def test_get_feedbackset_header_with_current_deadline_expired(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        groupcomment_builder = GroupCommentBuilder.make(
            feedback_set__deadline_datetime=DateTimeBuilder.now().minus(days=1))

        selector, request = self.__mock_http200_getrequest_htmls(role=groupcomment_builder.get_object().feedback_set.group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-current-deadline-expired'))

    def test_get_feedbackset_comment(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make()
        feedbackset_builder.add_groupcomment(
            user=janedoe,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
            text="hello world",
            published_datetime=timezone.now()
        )

        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-comment'))

    def test_get_feedbackset_comment_student(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make()
        feedbackset_builder.add_groupcomment(
            user=janedoe,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
            text="hello world",
            published_datetime=timezone.now()
        )

        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-comment-student'))

    def test_get_feedbackset_comment_examiner(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make()
        feedbackset_builder.add_groupcomment(
            user=janedoe,
            user_role='examiner',
            instant_publish=True,
            visible_for_students=True,
            text="hello world",
            published_datetime=timezone.now()
        )

        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-comment-examiner'))

    def test_get_feedbackset_comment_admin(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make()
        feedbackset_builder.add_groupcomment(
            user=janedoe,
            user_role='admin',
            instant_publish=True,
            visible_for_students=True,
            text="hello world",
            published_datetime=timezone.now()
        )

        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-comment-admin'))

    def test_get_feedbackset_comment_poster_fullname(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make()
        feedbackset_builder.add_groupcomment(
            user=janedoe,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
            text="hello world",
            published_datetime=timezone.now()
        )
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        name = selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(name, janedoe.fullname)

    def test_get_feedbackset_comment_poster_shortname(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make()
        feedbackset_builder.add_groupcomment(
            user=janedoe,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
        )
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        name = selector.one('.devilry-user-verbose-inline-shortname').alltext_normalized
        self.assertEquals(name, '({})'.format(janedoe.shortname))

    def test_get_feedbackset_comment_student_user_role(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        groupcomment_builder = GroupCommentBuilder.make(
            feedback_set__deadline_datetime=DateTimeBuilder.now(),
            user=janedoe,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
        )

        selector, request = self.__mock_http200_getrequest_htmls(role=groupcomment_builder.get_object().feedback_set.group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        role = selector.one('.comment-created-by-role-text').alltext_normalized
        self.assertEquals('({})'.format(groupcomment_builder.get_object().user_role), role)

    def test_get_feedbackset_comment_examiner_user_role(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        groupcomment_builder = GroupCommentBuilder.make(
            feedback_set__deadline_datetime=DateTimeBuilder.now(),
            user=janedoe,
            user_role='examiner',
            instant_publish=True,
            visible_for_students=True,
        )
        selector, request = self.__mock_http200_getrequest_htmls(role=groupcomment_builder.get_object().feedback_set.group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        role = selector.one('.comment-created-by-role-text').alltext_normalized
        self.assertEquals('({})'.format(groupcomment_builder.get_object().user_role), role)

    def test_get_feedbackset_comment_admin_user_role(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        groupcomment_builder = GroupCommentBuilder.make(
            feedback_set__deadline_datetime=DateTimeBuilder.now(),
            user=janedoe,
            user_role='admin',
            instant_publish=True,
            visible_for_students=True,
        )
        selector, request = self.__mock_http200_getrequest_htmls(role=groupcomment_builder.get_object().feedback_set.group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        role = selector.one('.comment-created-by-role-text').alltext_normalized
        self.assertEquals('({})'.format(groupcomment_builder.get_object().user_role), role)

    def test_get_feedbackfeed_event_without_any_deadlines_created(self):
        # Checks that when a feedbackset has been created and no first deadlines given, either on Assignment
        # or FeedbackSet, no 'created event' is rendered to template.
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make()
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertFalse(selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_get_feedbackfeed_event_without_any_deadlines_expired(self):
        # Checks that when a feedbackset has been created and no first deadlines given, either on Assignment
        # or FeedbackSet, no 'expired event' is rendered to template.
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make()
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertFalse(selector.exists('.devilry-group-feedbackfeed-event-message-deadline-expired'))

    def test_get_feedbackfeed_event_with_assignment_first_deadline_created(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make(
            group__assignment__first_deadline=timezone.now()+timezone.timedelta(days=1),
            deadline_datetime=timezone.now()+timezone.timedelta(days=1))
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_get_feedbackfeed_event_with_assignment_first_deadline_expired(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make(
            group__assignment__first_deadline=timezone.now()-timezone.timedelta(days=1),
            deadline_datetime=timezone.now()-timezone.timedelta(days=1))
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-event-message-deadline-expired'))

    def test_get_feedbackfeed_event_without_assignment_first_deadline_created(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make(
            deadline_datetime=timezone.now()+timezone.timedelta(days=1))
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_get_feedbackfeed_event_without_assignment_first_deadline_created(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make(
            deadline_datetime=timezone.now()-timezone.timedelta(days=1))
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-event-message-deadline-expired'))

    def test_get_feedbackfeed_event_without_feedbackfeed_deadline_datetime_created(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make(
            group__assignment__first_deadline=timezone.now()+timezone.timedelta(days=1))
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-event-message-deadline-created'))

    def test_get_feedbackfeed_event_without_feedbackfeed_deadline_datetime_expired(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make(
            group__assignment__first_deadline=timezone.now()-timezone.timedelta(days=1))
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-event-message-deadline-expired'))

    def test_get_feedbackset_event_delivery_passed(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        deadline = timezone.now()-timezone.timedelta(days=1)
        feedbackset_builder = FeedbackSetBuilder.make(
            group__assignment__first_deadline=deadline,
            group__assignment__max_points=10,
            group__assignment__passing_grade_min_points=5,
            published_datetime=timezone.now(),
            points=10,
            deadline_datetime=deadline
        )
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-event-message-passed'))

    def test_get_feedbackset_event_delivery_failed(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        feedbackset_builder = FeedbackSetBuilder.make(
            group__assignment__first_deadline=timezone.now()+timezone.timedelta(days=1),
            group__assignment__max_points=10,
            group__assignment__passing_grade_min_points=5,
            published_datetime=timezone.now(),
            deadline_datetime=timezone.now()+timezone.timedelta(days=1),
            points=1
        )
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-event-message-failed'))