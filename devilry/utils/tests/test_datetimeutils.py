from datetime import datetime

from django.test import TestCase

from devilry.utils import datetimeutils


class TestIsoformatNoseconds(TestCase):
    def test_sanity(self):
        self.assertEqual(
            '2015-12-24 17:42',
            datetimeutils.isoformat_noseconds(datetime(2015, 12, 24, 17, 42)))

    def test_no_seconds(self):
        self.assertEqual(
            '2015-12-24 17:42',
            datetimeutils.isoformat_noseconds(datetime(2015, 12, 24, 17, 42, 41)))

    def test_before_year_1900(self):
        self.assertEqual(
            '0030-12-24 14:30',
            datetimeutils.isoformat_noseconds(datetime(30, 12, 24, 14, 30)))


class TestIsoformatWithseconds(TestCase):
    def test_sanity(self):
        self.assertEqual(
            '2015-12-24 17:42:12',
            datetimeutils.isoformat_withseconds(datetime(2015, 12, 24, 17, 42, 12)))

    def test_before_year_1900(self):
        self.assertEqual(
            '0030-12-24 14:30:12',
            datetimeutils.isoformat_withseconds(datetime(30, 12, 24, 14, 30, 12)))


class TestDatetimeWithSameDayOfWeekAndTime(TestCase):
    def test_target_weekday_smaller_than_source(self):
        self.assertEqual(
            datetime(2015, 9, 25, 12, 30),  # Fri same week as target
            datetimeutils.datetime_with_same_day_of_week_and_time(
                weekdayandtimesource_datetime=datetime(2015, 9, 18, 12, 30),  # Fri
                target_datetime=datetime(2015, 9, 23, 0, 0)))   # Wed

    def test_target_weekday_larger_than_source_test1(self):
        self.assertEqual(
            datetime(2015, 9, 28, 12, 30),  # Mon week after target
            datetimeutils.datetime_with_same_day_of_week_and_time(
                weekdayandtimesource_datetime=datetime(2015, 9, 14, 12, 30),  # Mon
                target_datetime=datetime(2015, 9, 23, 0, 0)))   # Wed

    def test_target_weekday_larger_than_source_test2(self):
        self.assertEqual(
            datetime(2015, 9, 29, 12, 30),  # Tue week after target
            datetimeutils.datetime_with_same_day_of_week_and_time(
                weekdayandtimesource_datetime=datetime(2015, 9, 15, 12, 30),  # Tue
                target_datetime=datetime(2015, 9, 23, 0, 0)))   # Wed

    def test_target_weekday_same_as_source(self):
        self.assertEqual(
            datetime(2015, 9, 30, 12, 30),  # Wed week after target
            datetimeutils.datetime_with_same_day_of_week_and_time(
                weekdayandtimesource_datetime=datetime(2015, 9, 16, 12, 30),  # Wed
                target_datetime=datetime(2015, 9, 23, 0, 0)))   # Wed
