from django import test
from django.conf import settings
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_examiner.views.dashboard import assignmentlist


class TestAssignmentListView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = assignmentlist.AssignmentListView

    def test_title(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertIn(
            'Examiner dashboard',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            'Examiner dashboard',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_page_subheader(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            'Dashboard for the examiner role. You use this role to provide feedback to students.',
            mockresponse.selector.one('.devilry-page-subheader').alltext_normalized)
