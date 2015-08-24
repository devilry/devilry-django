from django.test import TestCase, RequestFactory
import htmls
import mock

from devilry.devilry_admin.views.assignment import overview
from devilry.project.develop.testhelpers.corebuilder import UserBuilder, AssignmentBuilder


class TestOverviewApp(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.factory = RequestFactory()
        self.assignmentbuilder = AssignmentBuilder.quickadd_ducku_duck1010_active_assignment1()

    def __mock_get_request(self, assignment):
        request = self.factory.get('/')
        request.user = self.testuser
        request.cradmin_role = assignment
        request.cradmin_app = mock.MagicMock()
        request.cradmin_instance = mock.MagicMock()
        request.session = mock.MagicMock()
        response = overview.Overview.as_view()(request)
        return response

    def __mock_http200_getrequest_htmls(self, assignment):
        response = self.__mock_get_request(assignment=assignment)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        return selector

    def test_title(self):
        selector = self.__mock_http200_getrequest_htmls(assignment=self.assignmentbuilder.assignment)
        self.assertEquals(selector.one('title').alltext_normalized, 'duck1010.active.assignment1')

    def test_h1(self):
        self.assignmentbuilder.update(long_name='DUCK 1010')
        selector = self.__mock_http200_getrequest_htmls(assignment=self.assignmentbuilder.assignment)
        self.assertEquals(selector.one('h1').alltext_normalized, 'DUCK 1010')
