from django.test import TestCase

from ..models import AssignmentGroup, Assignment, Candidate

class TestCandidate(TestCase):
    fixtures = ['core/deprecated_users.json', 'core/core.json']
    
    def test_non_anonymous(self):
        assignmentgroup1 = AssignmentGroup.objects.get(id=1)
        student1_candidate = Candidate.objects.get(id=1)
        self.assertEquals(student1_candidate.get_identifier(), "student1")
        
    def test_anonymous(self):
        oblig1 = Assignment.objects.get(id=1)
        # Set anonymous
        oblig1.anonymous = True
        oblig1.save()
        student1_candidate = Candidate.objects.get(id=1)
        self.assertEquals(student1_candidate.get_identifier(), "1")
