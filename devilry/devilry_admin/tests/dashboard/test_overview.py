from django.conf import settings
from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy
from devilry.devilry_admin.views.dashboard import overview


class TestOverviewApp(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def test_title(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser)
        self.assertEqual(u'Administrator dashboard',
                         mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser)
        self.assertEqual(u'Administrator dashboard',
                         mockresponse.selector.one('h1').alltext_normalized)
