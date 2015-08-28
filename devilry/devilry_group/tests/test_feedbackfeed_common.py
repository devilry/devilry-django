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

        # selector.one('.devilry-group-feedbackfeed-feed').prettyprint()
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-feed'))

    def test_get_without_first_deadline(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        group_builder = AssignmentGroupBuilder.make(assignment__first_deadline=None)
        selector, request = self.__mock_http200_getrequest_htmls(role=group_builder.get_object(),
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertFalse(selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))

    def test_get_with_first_deadline(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        group_builder = AssignmentGroupBuilder.make(assignment__first_deadline=timezone.now())
        selector, request = self.__mock_http200_getrequest_htmls(role=group_builder.get_object(),
                                                                 requestuser=requestuser,
                                                                 group=janedoe)

        # self.assertTrue(selector.exists('.devilry-group-feedbackfeed-current-current-deadline'))
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))

    def test_get_feedbackset_without_deadline_datetime(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        groupcomment_builder = GroupCommentBuilder.make(feedback_set__deadline_datetime=None)

        selector, request = self.__mock_http200_getrequest_htmls(role=groupcomment_builder.get_object().feedback_set.group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        # selector.one('.devilry-group-feedbackfeed-feed').prettyprint()
        self.assertFalse(selector.exists('.devilry-group-feedbackfeed-current-deadline-heading'))

    def test_get_feedbackset_with_current_deadline_not_expired(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        groupcomment_builder = GroupCommentBuilder.make(feedback_set__deadline_datetime=DateTimeBuilder.now().plus(days=1))

        selector, request = self.__mock_http200_getrequest_htmls(role=groupcomment_builder.get_object().feedback_set.group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        # selector.one('.devilry-group-feedbackfeed-feed').prettyprint()
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-current-deadline'))

    def test_get_feedbackset_with_current_deadline_expired(self):
        requestuser = UserBuilder2().user
        janedoe = UserBuilder2(fullname='Jane Doe').user
        groupcomment_builder = GroupCommentBuilder.make(feedback_set__deadline_datetime=DateTimeBuilder.now().minus(days=1))

        selector, request = self.__mock_http200_getrequest_htmls(role=groupcomment_builder.get_object().feedback_set.group,
                                                                 requestuser=requestuser,
                                                                 group=janedoe)
        self.assertTrue(selector.exists('.devilry-group-feedbackfeed-current-deadline-expired'))







    # def test_get_feedbackset_with_last_deadline(self):
    #     requestuser = UserBuilder2().user
    #     janedoe = UserBuilder2(fullname='Jane Doe').user
    #     groupcomment_builder = GroupCommentBuilder.make(feedback_set__group__assignment__first_deadline=timezone.now())
    #
    #     selector, request = self.__mock_http200_getrequest_htmls(role=groupcomment_builder.get_object().feedback_set.group,
    #                                                              requestuser=requestuser,
    #                                                              group=janedoe)
    #
    #     selector.one('.devilry-group-feedbackfeed-feed').prettyprint()
    #     self.assertFalse(1, 1)