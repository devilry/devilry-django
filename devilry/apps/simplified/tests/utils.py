from django.test import TestCase
from django.db.models import Q

from .. import utils


class TestUtils(TestCase):
    def test_create_q(self):
        self.assertEquals(utils._create_q("q", []), None)
        self.assertEquals(str(utils._create_q("q", ["a"])),
                str(Q(a__icontains="q")))
        self.assertEquals(str(utils._create_q("q", ["a", "b"])),
                str(Q(a__icontains="q")|Q(b__icontains="q")))

    def test_filter_orderby(self):
        self.assertEquals(utils._filter_orderby([], []), [])
        self.assertEquals(utils._filter_orderby([], ["a"]), [])
        self.assertEquals(utils._filter_orderby(["a", "b", "-c"], ["a"]),
                ["a"])
        self.assertEquals(
            utils._filter_orderby(["a", "b", "-c"], ["a", "c"]), ["a", "-c"])
