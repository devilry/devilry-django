from datetime import datetime
from django.test import TestCase

from devilry_detektor.models import DetektorAssignment
from devilry_detektor.tasks import run_detektor_on_assignment
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.corebuilder import PeriodBuilder


class TestRunDetektorOnAssignment(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('testassignment')

    def test_invalid_assignment(self):
        with self.assertRaises(DetektorAssignment.DoesNotExist):
            run_detektor_on_assignment.delay(
                assignment_id=200001).wait()

    def test_already_running(self):
        processing_started_datetime = datetime.now()
        DetektorAssignment.objects.create(
            assignment_id=self.assignmentbuilder.assignment.id,
            processing_started_by=self.testuser,
            processing_started_datetime=processing_started_datetime)

        run_detektor_on_assignment.delay(
            assignment_id=self.assignmentbuilder.assignment.id).wait()
        detektorassignment = DetektorAssignment.objects.all()[0]
        self.assertEqual(detektorassignment.processing_started_datetime, processing_started_datetime)

    def test_processing_detektorassignment_doesnotexist(self):
        with self.assertRaises(DetektorAssignment.DoesNotExist):
            run_detektor_on_assignment.delay(
                assignment_id=self.assignmentbuilder.assignment.id).wait()

    def test_processing_ok(self):
        DetektorAssignment.objects.create(
            assignment_id=self.assignmentbuilder.assignment.id,
            processing_started_by=self.testuser)

        otheruser = UserBuilder('otheruser').user
        self.assertEquals(DetektorAssignment.objects.count(), 1)
        run_detektor_on_assignment.delay(
            assignment_id=self.assignmentbuilder.assignment.id).wait()
        self.assertEquals(DetektorAssignment.objects.count(), 1)

        detektorassignment = DetektorAssignment.objects.all()[0]
        self.assertEqual(detektorassignment.processing_started_datetime, None)
