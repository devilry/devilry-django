from datetime import timedelta

from django import test
from django.conf import settings
from django.utils import timezone
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

    def test_not_assignments_where_not_examiner(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        # mommy.make('core.Examiner', user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_not_assignments_where_period_is_inactive(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', user=testuser,
                   assignmentgroup__parentnode__publishing_time=timezone.now() - timedelta(days=7),
                   assignmentgroup__parentnode__parentnode__start_time=timezone.now() - timedelta(days=10),
                   assignmentgroup__parentnode__parentnode__end_time=timezone.now() - timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_assignments_where_period_is_active(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', user=testuser,
                   assignmentgroup__parentnode__publishing_time=timezone.now() - timedelta(days=7),
                   assignmentgroup__parentnode__parentnode__start_time=timezone.now() - timedelta(days=10),
                   assignmentgroup__parentnode__parentnode__end_time=timezone.now() + timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))
