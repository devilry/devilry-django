# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# 3rd party imports
import mock
from model_mommy import mommy

# Django imports
from django import test

# CrAdmin imports
from django_cradmin import cradmin_testhelpers

# Devilry imports
from devilry.devilry_qualifiesforexam.views import list_statuses_view
from devilry.devilry_qualifiesforexam import models as status_models


class TestQualificationStatusPreviewTableRendering(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = list_statuses_view.ListStatusesView

    def test_title(self):
        testperiod = mommy.make(
                'core.Period',
                parentnode__short_name='testsubject',
                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'testsubject.testperiod')

    def test_heading(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEquals(
                mockresponse.selector.one('.devilry-qualifiesforexam-list-statuses-heading').alltext_normalized,
                'Status overview for {}'.format(testperiod))

    def test_create_new_status_button_text(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEquals(
                mockresponse.selector.one('#devilry_admin_period_createassignment_link').alltext_normalized,
                'Create new status')

    def test_links_urls(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(1, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEqual(
                mock.call(appname='qualifiesforexam', args=(), viewname='select-plugin', kwargs={}),
                mockresponse.request.cradmin_instance.reverse_url.call_args_list[0])

    def test_no_statuses_for_period_message(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        no_items_message = mockresponse.selector.one('.django-cradmin-listbuilderview-no-items-message')\
            .alltext_normalized
        self.assertEquals(no_items_message, 'No status has been created for this period yet.')

    def test_status_description_in_list(self):
        testperiod = mommy.make('core.Period')
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod, status=status_models.Status.READY)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEquals(
                mockresponse.selector.one('.devilry-qualifiesforexam-status-description-name').alltext_normalized,
                'Status')
        self.assertEquals(
                mockresponse.selector.one('.devilry-qualifiesforexam-status-description-date').alltext_normalized,
                teststatus.createtime.strftime('%A %B %-d, %Y, %H:%M'))

    def test_status_ready_in_list(self):
        testperiod = mommy.make('core.Period')
        mommy.make('devilry_qualifiesforexam.Status', period=testperiod, status=status_models.Status.READY)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertTrue(mockresponse.selector.one('.devilry-qualifiesforexam-list-statuses-statusitemframe'))
        self.assertEquals(mockresponse.selector.one('.label-success').alltext_normalized, 'Ready')

    def test_status_notready_in_list(self):
        testperiod = mommy.make('core.Period')
        mommy.make('devilry_qualifiesforexam.Status', period=testperiod, status=status_models.Status.NOTREADY)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertTrue(mockresponse.selector.one('.devilry-qualifiesforexam-list-statuses-statusitemframe'))
        self.assertEquals(mockresponse.selector.one('.label-warning').alltext_normalized, 'Not ready')

    def test_status_multiple_in_list(self):
        testperiod = mommy.make('core.Period')
        mommy.make('devilry_qualifiesforexam.Status',
                   period=testperiod, status=status_models.Status.READY,
                   _quantity=5)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        statuses = mockresponse.selector.list('.devilry-qualifiesforexam-list-statuses-statusitemframe')
        self.assertEquals(len(statuses), 5)

    def test_status_for_other_periods_not_listed(self):
        testperiod1 = mommy.make('core.Period')
        testperiod2 = mommy.make('core.Period')
        mommy.make('devilry_qualifiesforexam.Status', period=testperiod2, status=status_models.Status.READY)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod1)
        self.assertEquals(len(mockresponse.selector.list('.devilry-qualifiesforexam-list-statuses-statusitemframe')), 0)