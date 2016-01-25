from django.conf import settings
from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_frontpage.views import frontpage


class TestFrontpage(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = frontpage.FrontpageView

    def test_title(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(u'Devilry frontpage',
                         mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(u'Choose your role',
                         mockresponse.selector.one('h1').alltext_normalized)

    def test_user_is_student(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertTrue(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-student'))
        self.assertFalse(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-examiner'))
        self.assertFalse(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin'))

    def test_user_is_examiner(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertFalse(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-student'))
        self.assertTrue(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-examiner'))
        self.assertFalse(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin'))

    def test_user_is_superuser(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertFalse(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-student'))
        self.assertFalse(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-examiner'))
        self.assertTrue(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin'))
        self.assertTrue(mockresponse.selector.exists('.devilry-frontpage-superuser-link'))

    def test_user_is_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make(
                       'devilry_account.SubjectPermissionGroup',
                       permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN).permissiongroup)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertFalse(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-student'))
        self.assertFalse(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-examiner'))
        self.assertTrue(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin'))
        self.assertFalse(mockresponse.selector.exists('.devilry-frontpage-superuser-link'))

    def test_user_is_subjectadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make(
                       'devilry_account.SubjectPermissionGroup',
                       permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN).permissiongroup)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertFalse(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-student'))
        self.assertFalse(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-examiner'))
        self.assertTrue(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin'))
        self.assertFalse(mockresponse.selector.exists('.devilry-frontpage-superuser-link'))

    def test_user_is_periodadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make('devilry_account.PeriodPermissionGroup').permissiongroup)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertFalse(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-student'))
        self.assertFalse(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-examiner'))
        self.assertTrue(
            mockresponse.selector.exists('.devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin'))
        self.assertFalse(mockresponse.selector.exists('.devilry-frontpage-superuser-link'))
