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

    def test_bulkremove_examiners_from_groups(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        examineruser1 = UserBuilder('examineruser1').user
        examineruser2 = UserBuilder('examineruser2').user
        examineruser3 = UserBuilder('examineruser3').user
        group1builder = assignmentbuilder.add_group(
            examiners=[examineruser1])
        group2builder = assignmentbuilder.add_group(
            examiners=[examineruser1, examineruser2])
        group3builder = assignmentbuilder.add_group()
        group4builder = assignmentbuilder.add_group(
            examiners=[examineruser3])
        ignoredgroupbuilder = assignmentbuilder.add_group(examiners=[examineruser1])

        self.assertEquals(Examiner.objects.count(), 5)
        Examiner.objects.bulkremove_examiners_from_groups(
            [examineruser1, examineruser3],
            [group1builder.group, group2builder.group, group3builder.group, group4builder.group])
        self.assertEquals(Examiner.objects.count(), 2)
        self.assertEquals(
            set([examiner.assignmentgroup for examiner in Examiner.objects.all()]),
            set([ignoredgroupbuilder.group, group2builder.group]))
        group2builder.reload_from_db()
        self.assertEquals(group2builder.group.examiners.count(), 1)
        self.assertEquals(group2builder.group.examiners.all()[0].user, examineruser2)


    def test_randomdistribute_examiners_even(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        examineruser1 = UserBuilder('examineruser1').user
        examineruser2 = UserBuilder('examineruser2').user
        group1 = assignmentbuilder.add_group().group
        group2 = assignmentbuilder.add_group().group
        group3 = assignmentbuilder.add_group().group
        group4 = assignmentbuilder.add_group().group
        Examiner.objects.randomdistribute_examiners(
            examinerusers=[examineruser1, examineruser2],
            groups=[group1, group2, group3, group4])
        self.assertEquals(Examiner.objects.count(), 4)
        self.assertEquals(Examiner.objects.filter(user=examineruser1).count(), 2)
        self.assertEquals(Examiner.objects.filter(user=examineruser2).count(), 2)

    def test_randomdistribute_examiners_leftovers(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        examineruser1 = UserBuilder('examineruser1').user
        examineruser2 = UserBuilder('examineruser2').user
        group1 = assignmentbuilder.add_group().group
        group2 = assignmentbuilder.add_group().group
        group3 = assignmentbuilder.add_group().group
        Examiner.objects.randomdistribute_examiners(
            examinerusers=[examineruser1, examineruser2],
            groups=[group1, group2, group3])
        self.assertEquals(Examiner.objects.count(), 3)
        self.assertIn(Examiner.objects.filter(user=examineruser1).count(), [1, 2])
        self.assertIn(Examiner.objects.filter(user=examineruser2).count(), [1, 2])


    def test_setup_examiners_by_tags(self):
        periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        period = periodbuilder.period
        examineruser1 = UserBuilder('examineruser1').user
        examineruser2 = UserBuilder('examineruser2').user
        examineruser3 = UserBuilder('examineruser3').user
        examineruser4unused = UserBuilder('examineruser4unused').user
        period.relatedexaminer_set.create(
            user=examineruser1,
            tags='a,special')
        period.relatedexaminer_set.create(
            user=examineruser2,
            tags='b')
        period.relatedexaminer_set.create(
            user=examineruser3,
            tags='b,special')
        period.relatedexaminer_set.create( # Ignored (not sent into method)
            user=examineruser4unused,
            tags='b,special')

        assignmentbuilder = periodbuilder.add_assignment('assignment1')
        group1 = assignmentbuilder.add_group(tags=['a']).group
        group2 = assignmentbuilder.add_group(tags=['b']).group
        group3 = assignmentbuilder.add_group(tags=['b', 'special']).group
        group4 = assignmentbuilder.add_group().group
        group5 = assignmentbuilder.add_group(tags=['noexaminer']).group
        group6 = assignmentbuilder.add_group(tags=['b', 'special']).group # Ignored (not sent into method)

        self.assertEquals(Examiner.objects.count(), 0)
        Examiner.objects.setup_examiners_by_tags(
            period=period,
            examinerusers=[examineruser1, examineruser2, examineruser3],
            groups=[group1, group2, group3, group4, group5])
        self.assertEquals(Examiner.objects.count(), 6)

        def examinerusers_set(group):
            return set([e.user for e in group.examiners.all()])
        self.assertEquals(
            examinerusers_set(group1),
            set([examineruser1]))
        self.assertEquals(
            examinerusers_set(group2),
            set([examineruser2, examineruser3]))
        self.assertEquals(
            examinerusers_set(group3),
            set([examineruser1, examineruser2, examineruser3]))

        self.assertEquals(group4.examiners.count(), 0)
        self.assertEquals(group5.examiners.count(), 0)
        self.assertEquals(group6.examiners.count(), 0)
