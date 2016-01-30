# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import htmls
from django import test
from django_cradmin import datetimeutils
from model_mommy import mommy

from devilry.devilry_cradmin import devilry_listbuilder


class TestItemValue(test.TestCase):
    def test_title(self):
        testassignment = mommy.make('core.Assignment', long_name='Test Assignment')
        selector = htmls.S(devilry_listbuilder.assignment.ItemValue(value=testassignment).render())
        self.assertEqual(
                'Test Assignment',
                selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description(self):
        testassignment = mommy.make('core.Assignment',
                                    publishing_time=datetimeutils.default_timezone_datetime(2016, 12, 11),
                                    first_deadline=datetimeutils.default_timezone_datetime(2016, 12, 24, 18, 0))
        selector = htmls.S(devilry_listbuilder.assignment.ItemValue(value=testassignment).render())
        self.assertEqual(
                'First deadline: Saturday December 24, 2016, 18:00, '
                'Publishing time: Sunday December 11, 2016, 00:00',
                selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)
