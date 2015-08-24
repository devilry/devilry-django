from django.test import TestCase, RequestFactory
import htmls
import mock

from devilry.devilry_admin.views.node import overview
from devilry.project.develop.testhelpers.corebuilder import UserBuilder, NodeBuilder


class TestOverviewApp(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.factory = RequestFactory()
        self.nodebuilder = NodeBuilder('ducku')

    def __mock_get_request(self, node):
        request = self.factory.get('/')
        request.user = self.testuser
        request.cradmin_role = node
        request.cradmin_app = mock.MagicMock()
        request.cradmin_instance = mock.MagicMock()
        request.session = mock.MagicMock()
        response = overview.Overview.as_view()(request)
        return response

    def __mock_http200_getrequest_htmls(self, node):
        response = self.__mock_get_request(node=node)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        return selector

    def test_title(self):
        selector = self.__mock_http200_getrequest_htmls(node=self.nodebuilder.node)
        self.assertEquals(selector.one('title').alltext_normalized, 'ducku')

    def test_h1(self):
        self.nodebuilder.update(long_name='Duck U')
        selector = self.__mock_http200_getrequest_htmls(node=self.nodebuilder.node)
        self.assertEquals(selector.one('h1').alltext_normalized, 'Duck U')
