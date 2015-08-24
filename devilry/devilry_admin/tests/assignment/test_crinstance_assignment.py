from django.test import TestCase, RequestFactory

from devilry.apps.core.models import Assignment
from devilry.devilry_admin.cradmin_instances import crinstance_assignment
from devilry.project.develop.testhelpers.corebuilder import UserBuilder, NodeBuilder


class TestCrAdminInstance(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.nodebuilder = NodeBuilder.quickadd_ducku()
        self.subjectbuilder = self.nodebuilder.add_subject('duck1010')
        self.periodbuilder = self.subjectbuilder.add_6month_active_period()
        self.assignmentbuilder = self.periodbuilder.add_assignment('week1')

    def test_error_if_not_admin(self):
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_assignment.CrAdminInstance(request=request)
        with self.assertRaises(Assignment.DoesNotExist):
            instance.get_role_from_rolequeryset(role=self.testuser)

    def test_admin_on_assignment(self):
        self.assignmentbuilder.add_admins(self.testuser)
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_assignment.CrAdminInstance(request=request)
        self.assertEqual(
            instance.get_role_from_rolequeryset(role=self.assignmentbuilder.assignment),
            self.assignmentbuilder.assignment)

    def test_admin_on_period(self):
        self.periodbuilder.add_admins(self.testuser)
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_assignment.CrAdminInstance(request=request)
        self.assertEqual(
            instance.get_role_from_rolequeryset(role=self.assignmentbuilder.assignment),
            self.assignmentbuilder.assignment)

    def test_admin_on_subject(self):
        self.subjectbuilder.add_admins(self.testuser)
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_assignment.CrAdminInstance(request=request)
        self.assertEqual(
            instance.get_role_from_rolequeryset(role=self.assignmentbuilder.assignment),
            self.assignmentbuilder.assignment)

    def test_admin_on_node(self):
        self.nodebuilder.add_admins(self.testuser)
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_assignment.CrAdminInstance(request=request)
        self.assertEqual(
            instance.get_role_from_rolequeryset(role=self.assignmentbuilder.assignment),
            self.assignmentbuilder.assignment)
