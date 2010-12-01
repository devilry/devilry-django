from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils.simplejson import JSONDecoder
from django.db.models import Q

from devilry.core.models import Assignment

import utils
import examiner


class TestUtils(TestCase):
    def test_create_q(self):
        self.assertEquals(utils.create_q("q", []), None)
        self.assertEquals(str(utils.create_q("q", ["a"])),
                str(Q(a__icontains="q")))
        self.assertEquals(str(utils.create_q("q", ["a", "b"])),
                str(Q(a__icontains="q")|Q(b__icontains="q")))

    def test_filter_orderby(self):
        self.assertEquals(utils.filter_orderby([], []), [])
        self.assertEquals(utils.filter_orderby([], ["a"]), [])
        self.assertEquals(utils.filter_orderby(["a", "b", "-c"], ["a"]), ["a"])
        self.assertEquals(
            utils.filter_orderby(["a", "b", "-c"], ["a", "c"]), ["a", "-c"])


class TestExaminer(TestCase):
    fixtures = ["tests/simplified/data.json"]

    def test_assignments(self):
        examiner0 = User.objects.get(username="examiner0")
        all_assignments = Assignment.objects.all().order_by("short_name")
        qry = examiner.get_assignments(examiner0)
        self.assertEquals(len(qry), len(all_assignments))

        # search
        self.assertEquals(qry[0].short_name, all_assignments[0].short_name)
        qry = examiner.get_assignments(examiner0, search="ek")
        self.assertEquals(len(qry), 5)
        qry = examiner.get_assignments(examiner0, search="h0")
        self.assertEquals(len(qry), len(all_assignments))
        qry = examiner.get_assignments(examiner0, search="1100")
        self.assertEquals(len(qry), len(all_assignments))
