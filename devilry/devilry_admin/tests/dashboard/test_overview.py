import unittest

from django.conf import settings
from django.test import TestCase, RequestFactory
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker
from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_admin.views.dashboard import overview


class TestOverviewSubjectListViewApp(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.OverviewSubjectListView

    def test_title(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser)
        self.assertEqual('Administrator dashboard',
                         mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser)
        self.assertEqual('Administrator dashboard',
                         mockresponse.selector.one('h1').alltext_normalized)

    def __minimal_mockrequest_with_user(self, user):
        mockrequest = RequestFactory().get('')
        mockrequest.user = user
        view = overview.OverviewSubjectListView()
        view.request = mockrequest
        return view

    def __minimal_mockrequest_with_user_and_subjectpermissiongroup(self, user, subjectpermissiongroup):
        mockrequest = RequestFactory().get('')
        mockrequest.user = user
        mockrequest.subjectpermissiongroup = subjectpermissiongroup
        view = overview.OverviewSubjectListView()
        view.request = mockrequest
        return view

    def __minimal_mockrequest_with_user_and_periodpermissiongroup(self, user, periodpermissiongroup):
        mockrequest = RequestFactory().get('')
        mockrequest.user = user
        mockrequest.periodpermissiongroup = periodpermissiongroup
        view = overview.OverviewSubjectListView()
        view.request = mockrequest
        return view

    def __minimal_mockrequest_with_user_subjectpermissiongroup_and_periodpermissiongroup(
            self, user, subjectpermissiongroup, periodpermissiongroup):
        mockrequest = RequestFactory().get('')
        mockrequest.user = user
        mockrequest.subjectpermissiongroup = subjectpermissiongroup
        mockrequest.periodpermissiongroup = periodpermissiongroup
        view = overview.OverviewSubjectListView()
        view.request = mockrequest
        return view

    def test__get_all_subjects_where_user_is_subjectadmin_none(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        view = self.__minimal_mockrequest_with_user(user=testuser)
        self.assertEqual(
            [],
            list(view._OverviewSubjectListView__get_all_subjects_where_user_is_subjectadmin()))

    def test__get_all_subjects_where_user_is_subjectadmin_not_subjectadmin(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        permissiongroup = baker.make('devilry_account.PermissionGroup',
                                     grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        baker.make('devilry_account.SubjectPermissionGroup',
                   permissiongroup=permissiongroup)
        view = self.__minimal_mockrequest_with_user(user=testuser)
        self.assertEqual(
            [],
            list(view._OverviewSubjectListView__get_all_subjects_where_user_is_subjectadmin()))

    def test__get_all_subjects_where_user_is_subjectadmin_one_subjectadmin(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testsubject = baker.make('core.Subject')
        permissiongroup = baker.make('devilry_account.PermissionGroup',
                                     grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                     users=[testuser])
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup=permissiongroup,
                                            subject=testsubject)
        view = self.__minimal_mockrequest_with_user_and_subjectpermissiongroup(
            user=testuser, subjectpermissiongroup=subjectpermissiongroup)
        self.assertEqual(
            [testsubject],
            list(view._OverviewSubjectListView__get_all_subjects_where_user_is_subjectadmin()))

    def test__get_all_subjects_where_user_is_subjectadmin_several_subjectadmin(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testsubject1 = baker.make('core.Subject')
        testsubject2 = baker.make('core.Subject')
        permissiongroup = baker.make('devilry_account.PermissionGroup',
                                     grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                     users=[testuser])
        subjectpermissiongroup1 = baker.make('devilry_account.SubjectPermissionGroup',
                                             subject=testsubject1)
        subjectpermissiongroup2 = baker.make('devilry_account.SubjectPermissionGroup',
                                             permissiongroup=permissiongroup,
                                             subject=testsubject2)
        view = self.__minimal_mockrequest_with_user_and_subjectpermissiongroup(
            user=testuser, subjectpermissiongroup=[
                subjectpermissiongroup1,
                subjectpermissiongroup2])
        self.assertCountEqual(
            [testsubject2],
            list(view._OverviewSubjectListView__get_all_subjects_where_user_is_subjectadmin()))

    def test__get_all_subjects_where_user_is_subjectadmin_ordered_subjectadmin(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testsubject1 = baker.make('core.Subject', long_name="Course A")
        testsubject2 = baker.make('core.Subject', long_name="Course B")
        testsubject3 = baker.make('core.Subject', long_name="Course C")
        permissiongroup = baker.make('devilry_account.PermissionGroup',
                                     grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                     users=[testuser])
        subjectpermissiongroup1 = baker.make('devilry_account.SubjectPermissionGroup',
                                             permissiongroup=permissiongroup,
                                             subject=testsubject1)
        subjectpermissiongroup2 = baker.make('devilry_account.SubjectPermissionGroup',
                                             permissiongroup=permissiongroup,
                                             subject=testsubject2)
        subjectpermissiongroup3 = baker.make('devilry_account.SubjectPermissionGroup',
                                             permissiongroup=permissiongroup,
                                             subject=testsubject3)
        view = self.__minimal_mockrequest_with_user_and_subjectpermissiongroup(
            user=testuser, subjectpermissiongroup=[
                subjectpermissiongroup1,
                subjectpermissiongroup2,
                subjectpermissiongroup3])
        self.assertEqual(
            [testsubject1, testsubject2, testsubject3],
            list(view._OverviewSubjectListView__get_all_subjects_where_user_is_subjectadmin()))

    def test__get_all_periods_where_user_is_subjectadmin_or_periodadmin_none(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        view = self.__minimal_mockrequest_with_user(user=testuser)
        self.assertEqual(
            [],
              view._OverviewSubjectListView__get_all_periods_where_user_is_subjectadmin_or_periodadmin()
        )

    def test__get_all_periods_where_user_is_subjectadmin_or_periodadmin_not_periodadmin(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        permissiongroup = baker.make('devilry_account.PermissionGroup',
                                     grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN)
        baker.make('devilry_account.PeriodPermissionGroup',
                   permissiongroup=permissiongroup)
        view = self.__minimal_mockrequest_with_user(user=testuser)
        self.assertEqual(
            [],
            view._OverviewSubjectListView__get_all_periods_where_user_is_subjectadmin_or_periodadmin()
        )

    def test_get_all_periods_where_user_is_subjectadmin_or_periodadmin__one_periodadmin(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        permissiongroup = baker.make('devilry_account.PermissionGroup',
                                     grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN,
                                     users=[testuser])
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                           permissiongroup=permissiongroup,
                                           period=testperiod)
        view = self.__minimal_mockrequest_with_user_and_periodpermissiongroup(
            user=testuser, periodpermissiongroup=periodpermissiongroup
        )
        self.assertEqual(
            [[testperiod]],
            view._OverviewSubjectListView__get_all_periods_where_user_is_subjectadmin_or_periodadmin()
        )

    def test_get_all_periods_where_user_is_subjectadmin_or_periodadmin__several_periodadmin(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod1 = baker.make('core.Period')
        testperiod2 = baker.make('core.Period')
        permissiongroup = baker.make('devilry_account.PermissionGroup',
                                     grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN,
                                     users=[testuser])
        periodpermissiongroup1 = baker.make('devilry_account.PeriodPermissionGroup',
                                            permissiongroup=permissiongroup,
                                            period=testperiod1)
        periodpermissiongroup2 = baker.make('devilry_account.PeriodPermissionGroup',
                                            period=testperiod2)
        view = self.__minimal_mockrequest_with_user_and_periodpermissiongroup(
            user=testuser,
            periodpermissiongroup=[periodpermissiongroup1, periodpermissiongroup2]
        )
        self.assertEqual(
            [[testperiod1]],
            view._OverviewSubjectListView__get_all_periods_where_user_is_subjectadmin_or_periodadmin()
        )

    def test_get_all_periods_where_user_is_subjectadmin_or_periodadmin__ordered_periodadmin(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod1 = baker.make('core.Period', short_name="Period A")
        testperiod2 = baker.make('core.Period', short_name="Period C")
        testperiod3 = baker.make('core.Period', short_name="Period B")
        permissiongroup = baker.make('devilry_account.PermissionGroup',
                                     grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN,
                                     users=[testuser])
        periodpermissiongroup1 = baker.make('devilry_account.PeriodPermissionGroup',
                                            permissiongroup=permissiongroup,
                                            period=testperiod1)
        periodpermissiongroup2 = baker.make('devilry_account.PeriodPermissionGroup',
                                            permissiongroup=permissiongroup,
                                            period=testperiod2)
        periodpermissiongroup3 = baker.make('devilry_account.PeriodPermissionGroup',
                                            permissiongroup=permissiongroup,
                                            period=testperiod3)
        view = self.__minimal_mockrequest_with_user_and_periodpermissiongroup(
            user=testuser,
            periodpermissiongroup=[periodpermissiongroup1, periodpermissiongroup2, periodpermissiongroup3]
        )
        self.assertEqual(
            [[testperiod1], [testperiod3], [testperiod2]],
            view._OverviewSubjectListView__get_all_periods_where_user_is_subjectadmin_or_periodadmin()
        )

    def test_get_all_periods_where_user_is_subjectadmin_or_periodadmin__both(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod1 = baker.make('core.Period')
        testperiod2 = baker.make('core.Period')
        testsubject = baker.make('core.Subject')
        testperiod3 = baker.make('core.Period', parentnode=testsubject)
        permissiongroup1 = baker.make('devilry_account.PermissionGroup',
                                      grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN,
                                      users=[testuser])
        permissiongroup2 = baker.make('devilry_account.PermissionGroup',
                                      grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                      users=[testuser])
        periodpermissiongroup1 = baker.make('devilry_account.PeriodPermissionGroup',
                                            permissiongroup=permissiongroup1,
                                            period=testperiod1)
        periodpermissiongroup2 = baker.make('devilry_account.PeriodPermissionGroup',
                                            permissiongroup=permissiongroup1,
                                            period=testperiod2)
        periodpermissiongroup3 = baker.make('devilry_account.PeriodPermissionGroup',
                                            period=testperiod3)
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup=permissiongroup2,
                                            subject=testsubject)
        view = self.__minimal_mockrequest_with_user_subjectpermissiongroup_and_periodpermissiongroup(
            user=testuser,
            subjectpermissiongroup=subjectpermissiongroup,
            periodpermissiongroup=[periodpermissiongroup1, periodpermissiongroup2, periodpermissiongroup3]
        )
        self.assertCountEqual(
            [[testperiod2], [testperiod1], [testperiod3]],
            view._OverviewSubjectListView__get_all_periods_where_user_is_subjectadmin_or_periodadmin()
        )

    def test_get_all_periods_where_user_is_subjectadmin_or_periodadmin__both_ordered(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testsubject1 = baker.make('core.Subject', long_name="Course A")
        testsubject2 = baker.make('core.Subject', long_name="Course B")
        testperiod1 = baker.make('core.Period', short_name="Semester 2", parentnode=testsubject1)
        testperiod2 = baker.make('core.Period', short_name="Semester 1", parentnode=testsubject2)
        testperiod3 = baker.make('core.Period', short_name="Semester 1", parentnode=testsubject1)
        permissiongroup1 = baker.make('devilry_account.PermissionGroup',
                                      grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN,
                                      users=[testuser])
        permissiongroup2 = baker.make('devilry_account.PermissionGroup',
                                      grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                      users=[testuser])
        periodpermissiongroup1 = baker.make('devilry_account.PeriodPermissionGroup',
                                            permissiongroup=permissiongroup1,
                                            period=testperiod1)
        periodpermissiongroup2 = baker.make('devilry_account.PeriodPermissionGroup',
                                            permissiongroup=permissiongroup1,
                                            period=testperiod2)
        periodpermissiongroup3 = baker.make('devilry_account.PeriodPermissionGroup',
                                            period=testperiod3)
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup=permissiongroup2,
                                            subject=testsubject1)
        view = self.__minimal_mockrequest_with_user_subjectpermissiongroup_and_periodpermissiongroup(
            user=testuser,
            subjectpermissiongroup=subjectpermissiongroup,
            periodpermissiongroup=[periodpermissiongroup1, periodpermissiongroup2, periodpermissiongroup3]
        )
        self.assertCountEqual(
            [[testperiod3, testperiod2], [testperiod1]],
            view._OverviewSubjectListView__get_all_periods_where_user_is_subjectadmin_or_periodadmin()
        )

    # def test_empty_list(self):
    #     mockresponse = self.mock_http200_getrequest_htmls()
    #     self.assertTrue(mockresponse.selector.exists('.cradmin-legacy-listing-no-items-message'))
    #     self.assertFalse(mockresponse.selector.exists('.cradmin-legacy-listbuilder-list'))

    def test_nonempty_list(self):
        baker.make('core.Subject')
        requestuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.cradmin-legacy-listing-no-items-message'))
        self.assertTrue(mockresponse.selector.exists('.cradmin-legacy-listbuilder-list'))

    @unittest.skip('Must be fixed before it is commited to master')
    def test_default_ordering(self):
        baker.make('core.Subject', short_name='A')
        baker.make('core.Subject', short_name='B')
        baker.make('core.Subject', short_name='C')
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertEqual(
            'A',
            mockresponse.selector.one(
                '.cradmin-legacy-listbuilder-list li:nth-child(1)').alltext_normalized)
        self.assertEqual(
            'B',
            mockresponse.selector.one(
                '.cradmin-legacy-listbuilder-list li:nth-child(2)').alltext_normalized)
        self.assertEqual(
            'C',
            mockresponse.selector.one(
                '.cradmin-legacy-listbuilder-list li:nth-child(3)').alltext_normalized)

    def test_createsubject_button_not_superuser_not_rendered(self):
        baker.make('core.Subject')
        requestuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=False)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('#id_createsubject_button'))

    def test_createsubject_button_is_superuser_rendered(self):
        baker.make('core.Subject')
        requestuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertTrue(mockresponse.selector.exists('#id_createsubject_button'))
