from django.test import TestCase

from ..models import AssignmentGroup, Assignment, Candidate
from ..testhelper import TestHelper

class TestCandidate(TestCase, TestHelper):

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin)",
                 subjects=["inf1100"],
                 periods=["autumn"],
                 assignments=["assignment1"],
                 assignmentgroups=["g1:candidate(student1)"])
        # self.cand = Candidate(student=self.student1, candidate_id="1",
        #                       assignment_group=self.inf1100_autumn_assignment1_g1)

    def test_non_anonymous(self):
        self.assertEquals(self.inf1100_autumn_assignment1_g1.candidates.all()[0].get_identifier(), "student1")

    def test_anonymous(self):
        self.inf1100_autumn_assignment1.anonymous = True
        self.inf1100_autumn_assignment1.save()
        self.assertEquals(self.inf1100_autumn_assignment1_g1.candidates.all()[0].get_identifier(), str(self.student1.id))
