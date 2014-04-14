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
