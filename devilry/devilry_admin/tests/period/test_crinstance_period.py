from django.test import TestCase, RequestFactory

from devilry.apps.core.models import Period
from devilry.devilry_admin.cradmin_instances import crinstance_period
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder, UserBuilder, SubjectBuilder, NodeBuilder


class TestCrAdminInstance(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.nodebuilder = NodeBuilder.quickadd_ducku()
        self.subjectbuilder = self.nodebuilder.add_subject('duck1010')
        self.periodbuilder = self.subjectbuilder.add_6month_active_period()

    def test_error_if_not_admin(self):
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_period.CrAdminInstance(request=request)
        with self.assertRaises(Period.DoesNotExist):
            instance.get_role_from_rolequeryset(role=self.testuser)

    def test_admin_on_period(self):
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_period.CrAdminInstance(request=request)
        self.periodbuilder.add_admins(self.testuser)
        self.assertEqual(
            instance.get_role_from_rolequeryset(role=self.testuser),
            self.periodbuilder.period)

    def test_admin_on_subject(self):
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_period.CrAdminInstance(request=request)
        self.subjectbuilder.add_admins(self.testuser)
        self.assertEqual(
            instance.get_role_from_rolequeryset(role=self.testuser),
            self.periodbuilder.period)

    def test_admin_on_node(self):
        request = RequestFactory().get('/test')
        request.user = self.testuser
        instance = crinstance_period.CrAdminInstance(request=request)
        self.nodebuilder.add_admins(self.testuser)
        self.assertEqual(
            instance.get_role_from_rolequeryset(role=self.testuser),
            self.periodbuilder.period)
