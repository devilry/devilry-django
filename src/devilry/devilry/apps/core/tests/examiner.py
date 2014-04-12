from django.test import TestCase
from django.db import IntegrityError

from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry.apps.core.models import Examiner


class TestExaminer(TestCase):
    def test_bulkmake_examiner_for_groups(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        group1 = assignmentbuilder.add_group().group
        group2 = assignmentbuilder.add_group().group
        examineruser = UserBuilder('examineruser').user
        self.assertEquals(Examiner.objects.count(), 0)
        Examiner.objects.bulkmake_examiner_for_groups(examineruser, group1, group2)
        self.assertEquals(Examiner.objects.count(), 2)
        self.assertEquals(group1.examiners.count(), 1)
        self.assertEquals(group2.examiners.count(), 1)
        self.assertEquals(group1.examiners.all()[0].user, examineruser)
        self.assertEquals(group2.examiners.all()[0].user, examineruser)

    def test_bulkmake_examiner_for_groups_already_examiner(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        examineruser = UserBuilder('examineruser').user
        group1 = assignmentbuilder.add_group(
            examiners=[examineruser]).group

        self.assertEquals(Examiner.objects.count(), 1)
        with self.assertRaises(IntegrityError):
            Examiner.objects.bulkmake_examiner_for_groups(examineruser, group1)
        self.assertEquals(Examiner.objects.count(), 1)