from django.test import TestCase, RequestFactory

from devilry.apps.core.models import Subject
from devilry.devilry_admin.cradmin_instances import crinstance_subject
from devilry.project.develop.testhelpers.corebuilder import UserBuilder, NodeBuilder


class TestCrAdminInstance(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.nodebuilder = NodeBuilder.quickadd_ducku()
        self.subjectbuilder = self.nodebuilder.add_subject('duck1010')

    def test_error_if_not_admin(self):
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_subject.CrAdminInstance(request=request)
        with self.assertRaises(Subject.DoesNotExist):
            instance.get_role_from_rolequeryset(role=self.testuser)

    def test_admin_on_subject(self):
        self.subjectbuilder.add_admins(self.testuser)
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_subject.CrAdminInstance(request=request)
        self.assertEqual(
            instance.get_role_from_rolequeryset(role=self.subjectbuilder.subject),
            self.subjectbuilder.subject)

    def test_admin_on_node(self):
        self.nodebuilder.add_admins(self.testuser)
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_subject.CrAdminInstance(request=request)
        self.assertEqual(
            instance.get_role_from_rolequeryset(role=self.subjectbuilder.subject),
            self.subjectbuilder.subject)
