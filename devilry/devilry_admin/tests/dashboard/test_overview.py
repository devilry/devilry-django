from django.conf import settings
from django.test import TestCase, RequestFactory
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy
from devilry.devilry_account.models import PermissionGroup
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

    def __minimal_mockrequest_with_user(self, user):
        mockrequest = RequestFactory().get('')
        mockrequest.user = user
        view = overview.Overview()
        view.request = mockrequest
        return view

    def test__get_all_subjects_where_user_is_subjectadmin_none(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        view = self.__minimal_mockrequest_with_user(user=testuser)
        self.assertEqual(
            [],
            view._Overview__get_all_subjects_where_user_is_subjectadmin())

    def test__get_all_subjects_where_user_is_subjectadmin_not_subjectadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        permissiongroup = mommy.make('devilry_account.PermissionGroup',
                                     grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        mommy.make('devilry_account.SubjectPermissionGroup',
                   permissiongroup=permissiongroup)
        view = self.__minimal_mockrequest_with_user(user=testuser)
        self.assertEqual(
            [],
            view._Overview__get_all_subjects_where_user_is_subjectadmin())
