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
                 assignmentgroups=["g1:candidate(student1;5)"])

    def test_update_identifier(self):
        candidate = self.inf1100_autumn_assignment1_g1.candidates.all()[0]
        candidate.update_identifier(True)
        self.assertEquals(candidate.get_identifier(), candidate.candidate_id)
        candidate.update_identifier(False)
        self.assertEquals(candidate.get_identifier(), candidate.student.username)
 
    def test_non_anonymous(self):
        candidate = self.inf1100_autumn_assignment1_g1.candidates.all()[0]
        self.assertEquals(candidate.get_identifier(), candidate.student.username)
   
    def test_anonymous(self):
        cands = self.inf1100_autumn_assignment1_g1.candidates.all()
        self.inf1100_autumn_assignment1.anonymous = True
        self.inf1100_autumn_assignment1.save()
        candidate = self.inf1100_autumn_assignment1_g1.candidates.all()[0]
        self.assertEquals(candidate.get_identifier(),
                          str(candidate.candidate_id))

    def test_etag_update(self):
        etag = datetime.now()
        candidate = self.inf1100_autumn_assignment1_g1.candidates.all()[0]
        candidate.identifier = "Test_ID"
        self.assertRaises(EtagMismatchException, candidate.etag_update, etag)
        try:
            candidate.etag_update(etag)
        except EtagMismatchException as e:
            # Should not raise exception
            candidate.etag_update(e.etag)
        candidate_db = Candidate.objects.get(id=candidate.id)
        self.assertEquals(candidate_db.identifier, "Test_ID")
