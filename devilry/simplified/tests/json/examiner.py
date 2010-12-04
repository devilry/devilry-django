from django.test import TestCase
from django.contrib.auth.models import User

from devilry.core.models import Assignment
from devilry.simplified import examiner


class TestJsonExaminer(TestCase):
    fixtures = ["tests/simplified/data.json"]

    def test_list_assignments(self):
        examiner0 = User.objects.get(username="examiner0")
        all_assignments = Assignment.objects.all().order_by("short_name")
        qry = examiner.ListAssignments.list(examiner0)
        self.assertEquals(len(qry), len(all_assignments))

        # search
        self.assertEquals(qry[0].short_name, all_assignments[0].short_name)
        qry = examiner.ListAssignments.list(examiner0, search="ek")
        self.assertEquals(len(qry), 5)
        qry = examiner.ListAssignments.list(examiner0, search="h0")
        self.assertEquals(len(qry), len(all_assignments))
        qry = examiner.ListAssignments.list(examiner0, search="1100")
        self.assertEquals(len(qry), len(all_assignments))
