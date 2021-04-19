

from django.conf import settings
from django.test import TestCase
from cradmin_legacy import cradmin_testhelpers
from cradmin_legacy import crinstance
from model_bakery import baker

from devilry.apps.core.baker_recipes import ACTIVE_PERIOD_START, ACTIVE_PERIOD_END
from devilry.devilry_admin.views.subject_for_period_admin import overview_for_periodadmin
from devilry.utils import datetimeutils


class TestOverview(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview_for_periodadmin.Overview

    def test_title(self):
        testsubject = baker.make('core.Subject',
                                 short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual('testsubject',
                         mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testsubject = baker.make('core.Subject',
                                 long_name='Test Subject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual('Test Subject',
                         mockresponse.selector.one('h1').alltext_normalized)

    def test_period_list_one_period_where_user_is_period_admin(self):
        testperiod = baker.make('core.Period', long_name='Test period')
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup', period=testperiod)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod.parentnode,
            requestuser = testuser
        )
        self.assertEqual('Test period',
                         mockresponse.selector.one(
                             '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_period_list_should_only_see_periods_where_user_is_period_admin(self):
        testperiod = baker.make('core.Period', long_name='Test period')
        testperiod2 = baker.make('core.Period', long_name='Test period 2', parentnode=testperiod.parentnode)
        testperiod3 = baker.make('core.Period', long_name='Test period 3', parentnode=testperiod.parentnode)
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        periodpermissiongroup2 = baker.make('devilry_account.PeriodPermissionGroup',
                                            period=testperiod2)
        baker.make('devilry_account.PeriodPermissionGroup', period=testperiod3)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup2.permissiongroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod.parentnode,
            requestuser=testuser
        )
        periodlist = [x.alltext_normalized for x in
                      mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue-titledescription-title') ]
        self.assertEqual(['Test period 2', 'Test period'], periodlist)

    def test_periodlist_no_periods(self):
        testsubject = baker.make('core.Subject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertFalse(mockresponse.selector.exists('#devilry_admin_period_overview_periodlist'))

    def test_periodlist_itemrendering_name(self):
        testsubject = baker.make('core.Subject')
        testperiod = baker.make_recipe('devilry.apps.core.period_active',
                                       parentnode=testsubject,
                                       long_name='Test Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup', period=testperiod)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject, requestuser=testuser)
        self.assertEqual('Test Period',
                         mockresponse.selector.one(
                             '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_periodlist_itemrendering_url(self):
        testsubject = baker.make('core.Subject')
        testperiod = baker.make_recipe('devilry.apps.core.period_active',
                                       parentnode=testsubject,
                                       long_name='Test Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup', period=testperiod)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject, requestuser=testuser)
        self.assertEqual(crinstance.reverse_cradmin_url(instanceid='devilry_admin_periodadmin',
                                                        appname='overview',
                                                        roleid=testperiod.id),
                         mockresponse.selector.one(
                             '.devilry-admin-period-overview-perioditemframe')['href'])

    def test_periodlist_itemrendering_start_time(self):
        testsubject = baker.make('core.Subject')
        testperiod = baker.make_recipe('devilry.apps.core.period_active', parentnode=testsubject)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        with self.settings(DATETIME_FORMAT=datetimeutils.ISODATETIME_DJANGOFORMAT, USE_L10N=False):
            mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject, requestuser=testuser)
        self.assertEqual(datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_START),
                         mockresponse.selector.one(
                             '.devilry-cradmin-perioditemvalue-start-time-value').alltext_normalized)

    def test_periodlist_itemrendering_end_time(self):
        testsubject = baker.make('core.Subject')
        testperiod = baker.make_recipe('devilry.apps.core.period_active',
                                       parentnode=testsubject)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup', period=testperiod)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        with self.settings(DATETIME_FORMAT=datetimeutils.ISODATETIME_DJANGOFORMAT, USE_L10N=False):
            mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject, requestuser=testuser)
        self.assertEqual(datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                         mockresponse.selector.one(
                             '.devilry-cradmin-perioditemvalue-end-time-value').alltext_normalized)

    def test_periodlist_ordering(self):
        testsubject = baker.make('core.Subject')
        testperiod1 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode=testsubject,
                                        long_name='Period 2')
        testperiod2 = baker.make_recipe('devilry.apps.core.period_old',
                                        parentnode=testsubject,
                                        long_name='Period 1')
        testperiod3 = baker.make_recipe('devilry.apps.core.period_future',
                                        parentnode=testsubject,
                                        long_name='Period 3')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup1 = baker.make('devilry_account.PeriodPermissionGroup', period=testperiod1)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup1.permissiongroup)
        periodpermissiongroup2 = baker.make('devilry_account.PeriodPermissionGroup', period=testperiod2)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup2.permissiongroup)
        periodpermissiongroup3 = baker.make('devilry_account.PeriodPermissionGroup', period=testperiod3)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup3.permissiongroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject, requestuser=testuser)
        periodnames = [
            element.alltext_normalized
            for element in mockresponse.selector.list(
                '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual([
            'Period 3',
            'Period 2',
            'Period 1',
        ], periodnames)

    def test_periodlist_only_periods_in_subject(self):
        testsubject = baker.make('core.Subject')
        othersubject = baker.make('core.Subject')
        testperiod1 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode=testsubject,
                                        long_name='Testsubject Period 1')
        testperiod2 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode=othersubject,
                                        long_name='Othersubject Period 1')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod1)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        periodpermissiongroup2 = baker.make('devilry_account.PeriodPermissionGroup',
                                            period=testperiod2)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup2.permissiongroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject, requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue-titledescription-title')
        )
        self.assertEqual(
            'Testsubject Period 1',
            mockresponse.selector.one(
                '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized
        )
