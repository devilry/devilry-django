from datetime import datetime

from django.test import TestCase

from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry.apps.core.models import Candidate
from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models.model_utils import EtagMismatchException


class TestCandidate(TestCase):
    def test_bulkadd_candidates_to_groups(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        group1builder = assignmentbuilder.add_group()
        group2builder = assignmentbuilder.add_group()
        user1 = UserBuilder('user1').user
        user2 = UserBuilder('user2').user
        user3 = UserBuilder('user3').user
        self.assertEquals(Candidate.objects.count(), 0)
        Candidate.objects.bulkadd_candidates_to_groups(
            groups=[group1builder.group, group2builder.group],
            grouped_candidates=[
                [Candidate(student=user1), Candidate(student=user2)],
                [Candidate(student=user3)]
            ])
        self.assertEquals(Candidate.objects.count(), 3)
        group1builder.reload_from_db()
        group2builder.reload_from_db()
        self.assertEquals(group1builder.group.candidates.all().count(), 2)
        self.assertEquals(set([c.student for c in group1builder.group.candidates.all()]),
            set([user1, user2])) 
        self.assertEquals(group2builder.group.candidates.all().count(), 1)
        self.assertEquals(group2builder.group.candidates.all()[0].student, user3)
        with self.assertRaises(Candidate.DoesNotExist):
            candidate = group1builder.group.only_candidate
        self.assertEquals(group2builder.group.only_candidate.student, user3)



class TestCandidateOld(TestCase, TestHelper):
    """
    Do NOT add new tests here, add them to TestCandidate.
    """

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
