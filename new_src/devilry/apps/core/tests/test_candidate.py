from datetime import datetime

from django.test import TestCase

from ..models import Candidate
from ..testhelper import TestHelper
from ..models.model_utils import EtagMismatchException

class TestCandidate(TestCase, TestHelper):

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin)",
                 subjects=["inf1100"],
                 periods=["autumn"],
                 assignments=["assignment1"],
                 assignmentgroups=["g1:candidate(student1;5,student2)"])

    def test_update_identifier(self):
        candidate = self.inf1100_autumn_assignment1_g1.candidates.all()[0]
        candidate.update_identifier(True)
        self.assertEquals(candidate.identifier, candidate.candidate_id)
        candidate.update_identifier(False)
        self.assertEquals(candidate.identifier, candidate.student.username)

    def test_non_anonymous(self):
        candidate = self.inf1100_autumn_assignment1_g1.candidates.all()[0]
        self.assertEquals(candidate.identifier, candidate.student.username)

    def test_change_anonymous(self):
        cands = self.inf1100_autumn_assignment1_g1.candidates.all()
        self.inf1100_autumn_assignment1.anonymous = True
        self.inf1100_autumn_assignment1.save()
        candidate = self.inf1100_autumn_assignment1_g1.candidates.all()[0]
        self.assertEquals(candidate.identifier, candidate.candidate_id)
        # Test setting back to non-anomymous
        self.inf1100_autumn_assignment1.anonymous = False
        self.inf1100_autumn_assignment1.save()
        candidate = self.inf1100_autumn_assignment1_g1.candidates.all()[0]
        self.assertEquals(candidate.identifier, candidate.student.username)

    def test_anonymous_no_id(self):
        cands = self.inf1100_autumn_assignment1_g1.candidates.all()
        self.inf1100_autumn_assignment1.anonymous = True
        self.inf1100_autumn_assignment1.save()
        candidate = self.inf1100_autumn_assignment1_g1.candidates.all()[1]
        self.assertEquals(candidate.identifier, "candidate-id missing")

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

    def test_sync_candidate_with_user_on_change(self):
        candidate = self.inf1100_autumn_assignment1_g1.candidates.all()[0]
        self.assertEquals(candidate.identifier, 'student1')
        self.assertEquals(candidate.email, 'student1@example.com')
        candidate.student.username = 'changed'
        candidate.student.email = 'somethingchanged@example.com'
        candidate.student.save()
        candidate_db = Candidate.objects.get(id=candidate.id) # Must be re-fetched to avoid reading student from cache
        self.assertEquals(candidate_db.identifier, 'changed')
        self.assertEquals(candidate_db.email, 'somethingchanged@example.com')

    def test_sync_candidate_with_userprofile_on_change(self):
        candidate = self.inf1100_autumn_assignment1_g1.candidates.all()[0]
        self.assertEquals(candidate.full_name, None)
        candidate.student.devilryuserprofile.full_name = 'Changed Name'
        candidate.student.devilryuserprofile.save()
        candidate_db = Candidate.objects.get(id=candidate.id) # Must be re-fetched to avoid reading student from cache
        self.assertEquals(candidate_db.full_name, 'Changed Name')

    def test_displayname(self):
        peterpan = self.create_user('peterpan', fullname='Peter Pan')
        g1 = self.inf1100_autumn_assignment1_g1
        candidate = g1.candidates.create(student=peterpan)
        self.assertEquals(candidate.displayname, 'Peter Pan')

        peterpan.devilryuserprofile.full_name = None
        peterpan.devilryuserprofile.save()
        self.assertEquals(Candidate.objects.get(id=candidate.id).displayname, 'peterpan')
        g1.parentnode.anonymous = True
        g1.parentnode.save()
        self.assertEquals(Candidate.objects.get(id=candidate.id).displayname, 'candidate-id missing')
