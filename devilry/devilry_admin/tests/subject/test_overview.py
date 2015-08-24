from django.test import TestCase, RequestFactory
import htmls
import mock

from devilry.devilry_admin.views.subject import overview
from devilry.project.develop.testhelpers.corebuilder import UserBuilder, SubjectBuilder


class TestOverviewApp(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.factory = RequestFactory()
        self.subjectbuilder = SubjectBuilder.quickadd_ducku_duck1010()

    def __mock_get_request(self, subject):
        request = self.factory.get('/')
        request.user = self.testuser
        request.cradmin_role = subject
        request.cradmin_app = mock.MagicMock()
        request.cradmin_instance = mock.MagicMock()
        request.session = mock.MagicMock()
        response = overview.Overview.as_view()(request)
        return response

    def __mock_http200_getrequest_htmls(self, subject):
        response = self.__mock_get_request(subject=subject)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        return selector

    def test_title(self):
        selector = self.__mock_http200_getrequest_htmls(subject=self.subjectbuilder.subject)
        self.assertEquals(selector.one('title').alltext_normalized, 'duck1010')

    def test_h1(self):
        self.subjectbuilder.update(long_name='DUCK 1010')
        selector = self.__mock_http200_getrequest_htmls(subject=self.subjectbuilder.subject)
        self.assertEquals(selector.one('h1').alltext_normalized, 'DUCK 1010')
