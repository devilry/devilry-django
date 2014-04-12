from django.test import TestCase
from django.db import IntegrityError

from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry.apps.core.models import Examiner


class TestExaminer(TestCase):
    def test_bulkadd_examiners_to_groups(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        group1 = assignmentbuilder.add_group().group
        group2 = assignmentbuilder.add_group().group
        examineruser1 = UserBuilder('examineruser1').user
        examineruser2 = UserBuilder('examineruser2').user
        self.assertEquals(Examiner.objects.count(), 0)
        Examiner.objects.bulkadd_examiners_to_groups(
            examinerusers=[examineruser1, examineruser2],
            groups=[group1, group2])
        self.assertEquals(Examiner.objects.count(), 4)
        self.assertEquals(group1.examiners.count(), 2)
        self.assertEquals(group2.examiners.count(), 2)
        self.assertEquals(
            set([e.user for e in group1.examiners.all()]),
            set([examineruser1, examineruser2]))

    def test_bulkadd_examiners_to_groups_already_examiner(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        examineruser = UserBuilder('examineruser').user
        group1 = assignmentbuilder.add_group(
            examiners=[examineruser]).group

        self.assertEquals(Examiner.objects.count(), 1)
        with self.assertRaises(IntegrityError):
            Examiner.objects.bulkadd_examiners_to_groups(
                examinerusers=[examineruser],
                groups=[group1])
        self.assertEquals(Examiner.objects.count(), 1)


    def test_bulkclear_examiners_from_groups(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        examineruser1 = UserBuilder('examineruser1').user
        examineruser2 = UserBuilder('examineruser2').user
        group1 = assignmentbuilder.add_group(
            examiners=[examineruser1]).group
        group2 = assignmentbuilder.add_group(
            examiners=[examineruser1, examineruser2]).group
        group3 = assignmentbuilder.add_group().group
        ignoredgroup = assignmentbuilder.add_group(
            examiners=[examineruser1]).group
        self.assertEquals(Examiner.objects.count(), 4)
        Examiner.objects.bulkclear_examiners_from_groups([group1, group2, group3])
        self.assertEquals(Examiner.objects.count(), 1)
        self.assertEquals(Examiner.objects.all()[0].assignmentgroup, ignoredgroup)
