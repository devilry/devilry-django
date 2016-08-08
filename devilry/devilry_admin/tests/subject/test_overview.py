from __future__ import unicode_literals

import mock
from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from django_cradmin import crinstance
from model_mommy import mommy

from devilry.apps.core.mommy_recipes import ACTIVE_PERIOD_START, ACTIVE_PERIOD_END
from devilry.devilry_admin.views.subject import overview
from devilry.utils import datetimeutils


class TestOverview(TestCase, cradmin_testhelpers.TestCaseMixin):
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
        self.assertEqual('Create new semester',
                         mockresponse.selector.one(
                             '#devilry_admin_period_createperiod_link').alltext_normalized)

    def test_link_urls(self):
        testsubject = mommy.make('core.Subject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(3, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEqual(
                mock.call(appname=u'edit', args=(), viewname=u'INDEX', kwargs={}),
                mockresponse.request.cradmin_instance.reverse_url.call_args_list[0])
        self.assertEqual(
                mock.call(appname=u'createperiod', args=(), viewname=u'INDEX', kwargs={}),
                mockresponse.request.cradmin_instance.reverse_url.call_args_list[1])
        self.assertEqual(
                mock.call(appname=u'admins', args=(), viewname=u'INDEX', kwargs={}),
                mockresponse.request.cradmin_instance.reverse_url.call_args_list[2])

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
                             '.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

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
                             '.devilry-admin-period-overview-perioditemframe')['href'])

    def test_periodlist_itemrendering_start_time(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject)
        with self.settings(DATETIME_FORMAT=datetimeutils.ISODATETIME_DJANGOFORMAT, USE_L10N=False):
            mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_START),
                         mockresponse.selector.one(
                             '.devilry-cradmin-perioditemvalue-start-time-value').alltext_normalized)

    def test_periodlist_itemrendering_end_time(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_active',
                          parentnode=testsubject)
        with self.settings(DATETIME_FORMAT=datetimeutils.ISODATETIME_DJANGOFORMAT, USE_L10N=False):
            mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_END),
                         mockresponse.selector.one(
                             '.devilry-cradmin-perioditemvalue-end-time-value').alltext_normalized)

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
        periodnames = [
            element.alltext_normalized
            for element in mockresponse.selector.list(
                    '.django-cradmin-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual([
            'Period 3',
            'Period 2',
            'Period 1',
        ], periodnames)

    def test_periodlist_only_periods_in_subject(self):
        testsubject = mommy.make('core.Subject')
        othersubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_active',
                          parentnode=testsubject,
                          long_name='Testsubject Period 1')
        mommy.make_recipe('devilry.apps.core.period_active',
                          parentnode=othersubject,
                          long_name='Othersubject Period 1')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue-titledescription-title')
        )
        self.assertEqual(
            'Testsubject Period 1',
            mockresponse.selector.one(
                    '.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized
        )
