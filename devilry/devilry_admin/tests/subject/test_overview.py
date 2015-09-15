from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from django_cradmin import crinstance
from model_mommy import mommy

from devilry.apps.core.mommy_recipes import ACTIVE_PERIOD_START, ACTIVE_PERIOD_END
from devilry.devilry_admin.views.subject import overview
from devilry.utils import datetimeutils


class TestOverviewApp(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def test_title(self):
        testsubject = mommy.make('core.Subject',
                                 short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual('testsubject',
                         mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testsubject = mommy.make('core.Subject',
                                 long_name='Test Subject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(u'Test Subject',
                         mockresponse.selector.one('h1').alltext_normalized)

    def test_createperiod_link_text(self):
        testsubject = mommy.make('core.Subject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual('Create new period',
                         mockresponse.selector.one(
                             '#devilry_admin_period_createperiod_link').alltext_normalized)

    def test_createperiod_link_url(self):
        testsubject = mommy.make('core.Subject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        mockresponse.request.cradmin_instance.reverse_url.assert_called_once_with(
            appname='createperiod',
            viewname='INDEX',
            args=(), kwargs={})

    def test_periodlist_no_periods(self):
        testsubject = mommy.make('core.Subject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertFalse(mockresponse.selector.exists('#devilry_admin_period_overview_periodlist'))

    def test_periodlist_itemrendering_name(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_active',
                          parentnode=testsubject,
                          long_name='Test Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual('Test Period',
                         mockresponse.selector.one(
                             '.devilry-admin-period-overview-period-link').alltext_normalized)

    def test_periodlist_itemrendering_url(self):
        testsubject = mommy.make('core.Subject')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active',
                                       parentnode=testsubject,
                                       long_name='Test Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(crinstance.reverse_cradmin_url(instanceid='devilry_admin_periodadmin',
                                                        appname='overview',
                                                        roleid=testperiod.id),
                         mockresponse.selector.one(
                             '.devilry-admin-period-overview-period-link')['href'])

    def test_periodlist_itemrendering_start_time(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject)
        with self.settings(DATETIME_FORMAT=datetimeutils.ISODATETIME_DJANGOFORMAT, USE_L10N=False):
            mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_START),
                         mockresponse.selector.one(
                             '.devilry-admin-period-overview-period-start_time-value').alltext_normalized)

    def test_periodlist_itemrendering_end_time(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_active',
                          parentnode=testsubject)
        with self.settings(DATETIME_FORMAT=datetimeutils.ISODATETIME_DJANGOFORMAT, USE_L10N=False):
            mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                         mockresponse.selector.one(
                             '.devilry-admin-period-overview-period-end_time-value').alltext_normalized)

    def test_periodlist_ordering(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_active',
                          parentnode=testsubject,
                          long_name='Period 2')
        mommy.make_recipe('devilry.apps.core.period_old',
                          parentnode=testsubject,
                          long_name='Period 1')
        mommy.make_recipe('devilry.apps.core.period_future',
                          parentnode=testsubject,
                          long_name='Period 3')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        periodnames = [element.alltext_normalized
                       for element in mockresponse.selector.list('.devilry-admin-period-overview-period-link')]
        self.assertEqual([
            'Period 3',
            'Period 2',
            'Period 1',
        ], periodnames)
