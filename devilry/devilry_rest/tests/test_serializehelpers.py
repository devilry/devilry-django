from datetime import datetime
from unittest import TestCase

from devilry.devilry_rest.serializehelpers import format_timedelta, format_datetime


class TestRestFormat(TestCase):
    def test_format_datetime(self):
        self.assertEquals(format_datetime(datetime(2012, 1, 27, 14, 40, 45)),
                          '2012-01-27 14:40:45')

    def _test_delta(self, mk):
        self.assertEquals(format_timedelta(mk(datetime(2005, 5, 20, 15, 20, 0),
                                              datetime(2005, 5, 20, 15, 15, 0))),
                          {'days': 0, 'hours': 0, 'minutes': 5, 'seconds': 0})
        self.assertEquals(format_timedelta(mk(datetime(2005, 5, 20, 15, 0, 20),
                                              datetime(2005, 5, 20, 15, 0, 10))),
                          {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 10})
        self.assertEquals(format_timedelta(mk(datetime(2005, 5, 20, 15, 0, 0),
                                              datetime(2005, 5, 20, 14, 0, 0))),
                          {'days': 0, 'hours': 1, 'minutes': 0, 'seconds': 0})
        self.assertEquals(format_timedelta(mk(datetime(2005, 5, 20, 14, 0, 0),
                                              datetime(2005, 5, 19, 14, 0, 0))),
                          {'days': 1, 'hours': 0, 'minutes': 0, 'seconds': 0})
        self.assertEquals(format_timedelta(mk(datetime(2005, 5, 20, 14, 0, 0),
                                              datetime(2005, 2, 20, 14, 0, 0))),
                          {'days': 89, 'hours': 0, 'minutes': 0, 'seconds': 0})
        self.assertEquals(format_timedelta(mk(datetime(2005, 5, 20, 15, 20, 12),
                                              datetime(2005, 5, 20, 14, 0, 0))),
                          {'days': 0, 'hours': 1, 'minutes': 20, 'seconds': 12})

    def test_format_timedelta_positive(self):
        self._test_delta(lambda a, b: a-b)

    def test_format_timedelta_negative(self):
        self._test_delta(lambda a, b: b-a) # We just reverse the positive tests, and we should get the same results, since we only work with absolute values
