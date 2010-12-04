from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models import Q

from devilry.core.models import Assignment

import utils
import examiner


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
        self.assertEquals(utils._filter_orderby(["a", "b", "-c"], ["a"]), ["a"])
        self.assertEquals(
            utils._filter_orderby(["a", "b", "-c"], ["a", "c"]), ["a", "-c"])


class TestExaminer(TestCase):
    fixtures = ["tests/simplified/data.json"]

    def test_list_assignments(self):
        examiner0 = User.objects.get(username="examiner0")
        all_assignments = Assignment.objects.all().order_by("short_name")
        qry = examiner.list_assignments(examiner0)
        self.assertEquals(len(qry), len(all_assignments))

        # search
        self.assertEquals(qry[0].short_name, all_assignments[0].short_name)
        qry = examiner.list_assignments(examiner0, search="ek")
        self.assertEquals(len(qry), 5)
        qry = examiner.list_assignments(examiner0, search="h0")
        self.assertEquals(len(qry), len(all_assignments))
        qry = examiner.list_assignments(examiner0, search="1100")
        self.assertEquals(len(qry), len(all_assignments))

    def test_list_groups(self):
        examiner0 = User.objects.get(username="examiner0")
        assignment = Assignment.published_where_is_examiner(examiner0)[0]

        qry = examiner.list_groups(examiner0, assignment.id,
                orderby=["-id"], count=2)
        self.assertEquals(assignment.id, qry[0].parentnode.id)
        self.assertTrue(qry[0].id > qry[1].id)
        self.assertEquals(qry.count(), 2)

        qry = examiner.list_groups(examiner0, assignment.id,
                search="student0")
        self.assertEquals(qry.count(), 1)
        qry = examiner.list_groups(examiner0, assignment.id,
                search="thisisatest")
        self.assertEquals(qry.count(), 0)

        g = examiner.list_groups(examiner0, assignment.id)[0]
        g.name = "thisisatest"
        g.save()
        qry = examiner.list_groups(examiner0, assignment.id,
                search="thisisatest")
        self.assertEquals(qry.count(), 1)
