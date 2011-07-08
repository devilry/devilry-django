from datetime import datetime

from django.test import TestCase

from ..models import AssignmentGroup, Assignment, Candidate
from ..testhelper import TestHelper
from ..models.model_utils import EtagMismatchException

class TestCandidate(TestCase, TestHelper):

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin)",
                 subjects=["inf1100"],
                 periods=["autumn"],
                 assignments=["assignment1"],
                 assignmentgroups=["g1:candidate(student1)"])
        self.cand = Candidate(student=self.student1, candidate_id="1",
                              assignment_group=self.inf1100_autumn_assignment1_g1)

    def test_non_anonymous(self):
        self.assertEquals(self.cand.get_identifier(), "student1")

    def test_anonymous(self):
        self.inf1100_autumn_assignment1.anonymous = True
        self.inf1100_autumn_assignment1.save()
        self.assertEquals(self.cand.get_identifier(), "1")

    def test_etag_update(self):
        etag = datetime.now()
        obj = self.inf1100
        #obj.candidate_id = "Test_ID"
        self.assertRaises(EtagMismatchException, obj.etag_update, etag)
        try:
            obj.etag_update(etag)
        except EtagMismatchException as e:
            # Should not raise exception
            obj.etag_update(e.etag)
        #obj2 = Candidate.objects.get(id=obj.id)
        #self.assertEquals(obj2.candidate_id, "Test_ID")
