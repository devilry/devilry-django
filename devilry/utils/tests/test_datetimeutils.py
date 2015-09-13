from datetime import datetime

from django.test import TestCase

from devilry.utils import datetimeutils


class TestIsoformatNoseconds(TestCase):
    def test_sanity(self):
        self.assertEqual(
            '2015-12-24 17:42',
            datetimeutils.isoformat_noseconds(datetime(2015, 12, 24, 17, 42)))

    def test_no_secnds(self):
        self.assertEqual(
            '2015-12-24 17:42',
            datetimeutils.isoformat_noseconds(datetime(2015, 12, 24, 17, 42, 41)))

    def test_before_year_1900(self):
        self.assertEqual(
            '0030-12-24 14:30',
            datetimeutils.isoformat_noseconds(datetime(30, 12, 24, 14, 30)))

