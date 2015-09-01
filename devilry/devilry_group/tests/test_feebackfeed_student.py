from django.test import TestCase, RequestFactory
from django.utils import timezone
import htmls
import mock

from devilry.devilry_group.tests import test_feedbackfeed_common
from devilry.devilry_group.views import feedbackfeed_student
from devilry.project.develop.testhelpers.corebuilder import UserBuilder2, AssignmentGroupBuilder, FeedbackSetBuilder


class TestFeedbackfeedStudent(TestCase, test_feedbackfeed_common.TestFeedbackFeedMixin):
    viewclass = feedbackfeed_student.StudentFeedbackFeedView

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

    def test_get_feedbackset_comment_student_after_deadline(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        time = timezone.now()
        feedbackset_builder = FeedbackSetBuilder.make(
            group__assignment__first_deadline=time,
            deadline_datetime = time
        )
        feedbackset_builder.add_groupcomment(
            user=janedoe,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
            text="hello world",
            published_datetime=timezone.now()+timezone.timedelta(seconds=1)
        )
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.after-deadline-badge'))

    def test_get_feedbackset_comment_student_before_deadline(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        time = timezone.now()
        feedbackset_builder = FeedbackSetBuilder.make(
            group__assignment__first_deadline=time,
            deadline_datetime = time
        )
        feedbackset_builder.add_groupcomment(
            user=janedoe,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
            text="hello world",
            published_datetime=timezone.now()-timezone.timedelta(seconds=1)
        )
        selector, request = self.__mock_http200_getrequest_htmls(role=feedbackset_builder.get_object().group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertFalse(selector.exists('.after-deadline-badge'))