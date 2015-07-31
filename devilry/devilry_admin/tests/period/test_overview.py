from django.test import TestCase, RequestFactory
import htmls
import mock

from devilry.devilry_admin.views.period import overview
from devilry.project.develop.testhelpers.corebuilder import UserBuilder, PeriodBuilder


class TestOverviewApp(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.factory = RequestFactory()
        self.periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()

    def __mock_get_request(self, period):
        request = self.factory.get('/')
        request.user = self.testuser
        request.cradmin_role = period
        request.cradmin_app = mock.MagicMock()
        request.cradmin_instance = mock.MagicMock()
        request.session = mock.MagicMock()
        response = overview.Overview.as_view()(request)
        return response

    def __mock_http200_getrequest_htmls(self, period):
        response = self.__mock_get_request(period=period)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        return selector

    def test_title(self):
        selector = self.__mock_http200_getrequest_htmls(period=self.periodbuilder.period)
        self.assertEquals(selector.one('title').alltext_normalized, 'duck1010.active')

    def test_h1(self):
        self.periodbuilder.update(long_name='Active Semester')
        selector = self.__mock_http200_getrequest_htmls(period=self.periodbuilder.period)
        self.assertEquals(selector.one('h1').alltext_normalized, 'Duck1010 Active Semester')
