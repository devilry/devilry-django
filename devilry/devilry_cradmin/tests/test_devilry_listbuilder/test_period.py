# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import htmls
from django import test
from django_cradmin import datetimeutils
from model_mommy import mommy

from devilry.devilry_cradmin import devilry_listbuilder


class TestAdminItemValue(test.TestCase):
    def test_title(self):
        testperiod = mommy.make('core.Period', long_name='Test Period')
        selector = htmls.S(devilry_listbuilder.period.AdminItemValue(value=testperiod).render())
        self.assertEqual(
                'Test Period',
                selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description(self):
        testperiod = mommy.make('core.Period',
                                start_time=datetimeutils.default_timezone_datetime(2015, 1, 15),
                                end_time=datetimeutils.default_timezone_datetime(2015, 12, 24))
        selector = htmls.S(devilry_listbuilder.period.AdminItemValue(value=testperiod).render())
        self.assertEqual(
                'Thursday January 15, 2015, 00:00 \u2014 Thursday December 24, 2015, 00:00',
                selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)


class TestStudentItemValue(test.TestCase):
    def test_title(self):
        testperiod = mommy.make('core.Period',
                                parentnode__long_name='Test Subject',
                                long_name='Test Period')
        selector = htmls.S(devilry_listbuilder.period.StudentItemValue(value=testperiod).render())
        self.assertEqual(
                'Test Subject - Test Period',
                selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    # def test_description(self):
    #     testperiod = mommy.make('core.Period',
    #                             start_time=datetimeutils.default_timezone_datetime(2015, 1, 15),
    #                             end_time=datetimeutils.default_timezone_datetime(2015, 12, 24))
    #     selector = htmls.S(devilry_listbuilder.period.StudentItemValue(value=testperiod).render())
    #     self.assertEqual(
    #             'Thursday January 15, 2015, 00:00 \u2014 Thursday December 24, 2015, 00:00',
    #             selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)
