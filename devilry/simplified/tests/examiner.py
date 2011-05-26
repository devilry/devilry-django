from django.test import TestCase
from django.contrib.auth.models import User

from devilry.core import models
from devilry.simplified.examiner import Subjects, Assignments, Groups


class TestExaminerSubjects(TestCase):
    fixtures = ["tests/simplified/data.json"]

    def test_get(self):
        examiner0 = User.objects.get(username="examiner0")
        subjects = models.Subject.published_where_is_examiner(examiner0).order_by("short_name")
        qry = Subjects.getqry(examiner0).qry
        self.assertEquals(len(qry), len(subjects))
        self.assertEquals(qry[0].short_name, subjects[0].short_name)

        # query
        qry = Subjects.getqry(examiner0, query="duck1").qry
        self.assertEquals(len(qry), 2)
        qry = Subjects.getqry(examiner0, query="duck").qry
        self.assertEquals(len(qry), len(subjects))
        qry = Subjects.getqry(examiner0, query="1100").qry
        self.assertEquals(len(qry), 1)


class TestExaminerAssignments(TestCase):
    fixtures = ["tests/simplified/data.json"]

    def test_get(self):
        examiner0 = User.objects.get(username="examiner0")
        all_assignments = models.Assignment.objects.all().order_by("short_name")
        qry = Assignments.getqry(examiner0).qry
        self.assertEquals(len(qry), len(all_assignments))
        self.assertEquals(qry[0].short_name, all_assignments[0].short_name)

        # query
        qry = Assignments.getqry(examiner0, query="ek").qry
        self.assertEquals(len(qry), 9)
        qry = Assignments.getqry(examiner0, query="h0").qry
        self.assertEquals(len(qry), len(all_assignments))
        qry = Assignments.getqry(examiner0, query="1100").qry
        self.assertEquals(len(qry), 4)



class TestExaminerGroups(TestCase):
    fixtures = ["tests/simplified/data.json"]

    def test_get(self):
        examiner0 = User.objects.get(username="examiner0")
        assignment = models.Assignment.published_where_is_examiner(examiner0)[0]

        qry = Groups.getqry(examiner0, assignment.id,
                orderby=["-id"], limit=2).qry
        self.assertEquals(assignment.id, qry[0].parentnode.id)
        self.assertTrue(qry[0].id > qry[1].id)
        self.assertEquals(qry.count(), 2)

        qry = Groups.getqry(examiner0, assignment.id,
                query="student0").qry
        self.assertEquals(qry.count(), 1)
        qry = Groups.getqry(examiner0, assignment.id,
                query="thisisatest").qry
        self.assertEquals(qry.count(), 0)

        g = Groups.getqry(examiner0, assignment.id).qry[0]
        g.name = "thisisatest"
        g.save()
        qry = Groups.getqry(examiner0, assignment.id,
                query="thisisatest").qry
        self.assertEquals(qry.count(), 1)
