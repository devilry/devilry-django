# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from model_mommy import mommy
import re

from django import test
from django.utils import timezone

from devilry.utils import datetimeutils
from devilry.devilry_group.models import FeedbackSet


class URLDatetime(test.TestCase):

    def test_url_patternmatcher(self):
        self.assertIsNotNone(re.match(r'\w+', datetimeutils.datetime_to_string(timezone.now())))

    def test_url_convert_to_string_and_back(self):
        datetime_original = timezone.now().replace(microsecond=0)
        datetime_as_string = datetimeutils.datetime_to_string(datetime_original)
        datetime_converted_back = datetimeutils.string_to_datetime(datetime_as_string)
        self.assertEquals(datetime_original, datetime_converted_back)

    # def test_url_convert_feedbackset_datetime(self):
    #     fbset = mommy.make('devilry_group.FeedbackSet')
    #     fbset_deadline_datetime_string = datetimeutils.datetime_to_string(fbset.deadline_datetime)
    #     fbset_deadline_datetime_converted_back = datetimeutils.string_to_datetime(fbset_deadline_datetime_string)
    #     self.assertEquals(fbset_deadline_datetime_converted_back, fbset.deadline_datetime)
