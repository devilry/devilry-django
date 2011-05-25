from django.test import TestCase
from django.contrib.auth.models import User

from devilry.core.models import Assignment
from devilry.simplified.examiner import Assignments, Groups


class TestAssignments(TestCase):
    fixtures = ["tests/simplified/data.json"]

    def test_get(self):
        examiner0 = User.objects.get(username="examiner0")
        all_assignments = Assignment.objects.all().order_by("short_name")
        qry = Assignments.getqry(examiner0)
        self.assertEquals(len(qry), len(all_assignments))

        # search
        self.assertEquals(qry[0].short_name, all_assignments[0].short_name)
        qry = Assignments.getqry(examiner0, search="ek")
        self.assertEquals(len(qry), 9)
        qry = Assignments.getqry(examiner0, search="h0")
        self.assertEquals(len(qry), len(all_assignments))
        qry = Assignments.getqry(examiner0, search="1100")
        self.assertEquals(len(qry), 4)



class TestGroups(TestCase):
    fixtures = ["tests/simplified/data.json"]

    def test_get(self):
        examiner0 = User.objects.get(username="examiner0")
        assignment = Assignment.published_where_is_examiner(examiner0)[0]

        qry = Groups.getqry(examiner0, assignment.id,
                orderby=["-id"], count=2)
        self.assertEquals(assignment.id, qry[0].parentnode.id)
        self.assertTrue(qry[0].id > qry[1].id)
        self.assertEquals(qry.count(), 2)

        qry = Groups.getqry(examiner0, assignment.id,
                search="student0")
        self.assertEquals(qry.count(), 1)
        qry = Groups.getqry(examiner0, assignment.id,
                search="thisisatest")
        self.assertEquals(qry.count(), 0)

        g = Groups.getqry(examiner0, assignment.id)[0]
        g.name = "thisisatest"
        g.save()
        qry = Groups.getqry(examiner0, assignment.id,
                search="thisisatest")
        self.assertEquals(qry.count(), 1)
