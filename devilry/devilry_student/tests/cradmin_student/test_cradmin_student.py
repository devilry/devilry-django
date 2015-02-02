from django.test import TestCase, RequestFactory
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_student.cradmin_group import cradmin_group
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder, UserBuilder


class TestStudentCrAdminInstance(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        self.assignmentbuilder = self.periodbuilder.add_assignment('testassignment')
        self.groupbuilder = self.assignmentbuilder.add_group()

    def test_error_if_not_the_student(self):
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = cradmin_group.CrAdminInstance(request=request)
        otheruser = UserBuilder('otheruser').user
        with self.assertRaises(AssignmentGroup.DoesNotExist):
            instance.get_role_from_rolequeryset(role=otheruser)
