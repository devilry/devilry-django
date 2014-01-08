from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry.apps.core.models import PointRangeToGrade


class TestPointRangeToGradeManager(TestCase):
    def setUp(self):
        self.assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment')

    def test_filter_overlapping_ranges(self):
        assignment = self.assignmentbuilder.assignment
        pointrange_to_grade = assignment.pointrangetograde_set.create(
            minimum_points=10,
            maximum_points=20,
            grade='D'
        )
        self.assertFalse(PointRangeToGrade.objects.filter_overlapping_ranges(0, 9).exists())
        self.assertTrue(PointRangeToGrade.objects.filter_overlapping_ranges(10, 20).exists())
        self.assertTrue(PointRangeToGrade.objects.filter_overlapping_ranges(13, 18).exists())
        self.assertTrue(PointRangeToGrade.objects.filter_overlapping_ranges(18, 25).exists())
        self.assertTrue(PointRangeToGrade.objects.filter_overlapping_ranges(20, 21).exists())
        self.assertTrue(PointRangeToGrade.objects.filter_overlapping_ranges(8, 22).exists())
        self.assertFalse(PointRangeToGrade.objects.filter_overlapping_ranges(21, 22).exists())



class TestPointRangeToGrade(TestCase):
    def setUp(self):
        self.periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        self.assignmentbuilder = self.periodbuilder.add_assignment('assignment')

    def test_clean_max_smaller_than_min_fails(self):
        pointrange_to_grade = PointRangeToGrade(
            assignment=self.assignmentbuilder.assignment,
            minimum_points=2,
            maximum_points=1,
            grade='D'
        )
        with self.assertRaises(ValidationError):
            pointrange_to_grade.clean()

    def test_clean_max_equal_to_min_works(self):
        pointrange_to_grade = PointRangeToGrade(
            assignment=self.assignmentbuilder.assignment,
            minimum_points=1,
            maximum_points=1,
            grade='D'
        )
        with self.assertRaises(ValidationError):
            pointrange_to_grade.clean()

    def test_clean_max_greater_than_min_works(self):
        pointrange_to_grade = PointRangeToGrade(
            assignment=self.assignmentbuilder.assignment,
            minimum_points=0,
            maximum_points=1,
            grade='D'
        )
        pointrange_to_grade.clean() # Should work without error


    def test_clean_overlapping_other_on_same_assignment_fails(self):
        assignment = self.assignmentbuilder.assignment
        pointrange_to_grade = assignment.pointrangetograde_set.create(
            minimum_points=10,
            maximum_points=20,
            grade='D'
        )
        pointrange_to_grade = PointRangeToGrade(
            assignment=assignment,
            minimum_points=12,
            maximum_points=18,
            grade='C'
        )
        with self.assertRaises(ValidationError):
            pointrange_to_grade.clean()

    def test_clean_existing_does_not_match_overlapping_range(self):
        pointrange_to_grade = PointRangeToGrade(
            assignment=self.assignmentbuilder.assignment,
            minimum_points=12,
            maximum_points=18,
            grade='C'
        )
        pointrange_to_grade.save()
        pointrange_to_grade.clean()

    def test_clean_does_not_match_overlapping_range_in_other_assignments(self):
        assignment2 = self.periodbuilder.add_assignment('assignment2').assignment
        pointrange_to_grade = PointRangeToGrade(
            assignment=self.assignmentbuilder.assignment,
            minimum_points=12,
            maximum_points=18,
            grade='D'
        )
        PointRangeToGrade(
            assignment=assignment2,
            minimum_points=10,
            maximum_points=20,
            grade='C'
        ).save()
        pointrange_to_grade.clean()

    def test_clean_not_unique_grade(self):
        PointRangeToGrade(
            assignment=self.assignmentbuilder.assignment,
            minimum_points=1,
            maximum_points=2,
            grade='C'
        ).save()
        pointrange_to_grade = PointRangeToGrade(
            assignment=self.assignmentbuilder.assignment,
            minimum_points=5,
            maximum_points=6,
            grade='C'
        )
        with self.assertRaises(IntegrityError):
            pointrange_to_grade.save()

        # Does not fail when in another assignment
        assignment2 = self.periodbuilder.add_assignment('assignment2').assignment
        pointrange_to_grade = PointRangeToGrade(
            assignment=assignment2,
            minimum_points=5,
            maximum_points=6,
            grade='C'
        ).save()

    def test_ordering(self):
        assignment = self.assignmentbuilder.assignment
        f = assignment.pointrangetograde_set.create(
            minimum_points=0,
            maximum_points=20,
            grade='F'
        )
        e = assignment.pointrangetograde_set.create(
            minimum_points=21,
            maximum_points=40,
            grade='E'
        )
        d = assignment.pointrangetograde_set.create(
            minimum_points=41,
            maximum_points=50,
            grade='D'
        )
        self.assertEquals(list(PointRangeToGrade.objects.all()), [f, e, d])