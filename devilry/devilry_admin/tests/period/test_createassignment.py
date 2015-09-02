from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from devilry.devilry_admin.views.period import createassignment


class TestCreateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = createassignment.CreateView

    def test_get_render_formfields(self):
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertTrue(mockresponse.selector.exists('input[name=long_name]'))
        self.assertTrue(mockresponse.selector.exists('input[name=short_name]'))
        self.assertTrue(mockresponse.selector.exists('input[name=first_deadline_0]'))
        self.assertTrue(mockresponse.selector.exists('input[name=first_deadline_1]'))
