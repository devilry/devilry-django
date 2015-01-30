from django.http import Http404
from django.test import TestCase, RequestFactory
from devilry.devilry_student.cradmin_group import cradmin_group
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder, UserBuilder


class TestGroupCrAdminInstance(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        self.assignmentbuilder = self.periodbuilder.add_assignment('testassignment')
        self.groupbuilder = self.assignmentbuilder.add_group()

    def test_404_no_deadlines(self):
        self.groupbuilder.add_students(self.testuser)
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = cradmin_group.CrAdminInstance(request=request)
        with self.assertRaises(Http404):
            instance.get_role_from_rolequeryset(role=self.groupbuilder.group)
