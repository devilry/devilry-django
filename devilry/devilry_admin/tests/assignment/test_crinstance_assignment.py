from django.conf import settings
from django.test import TestCase, RequestFactory
from model_mommy import mommy

from devilry.devilry_admin.views.assignment import crinstance_assignment


class TestCrAdminInstance(TestCase):
    def test_get_rolequeryset_not_admin(self):
        mommy.make('core.Assignment')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        request = RequestFactory().get('/test')
        request.user = testuser
        instance = crinstance_assignment.CrAdminInstance(request=request)
        self.assertEqual([], list(instance.get_rolequeryset()))

    def test_get_rolequeryset_superuser(self):
        testassignment = mommy.make('core.Assignment')
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        request = RequestFactory().get('/test')
        request.user = testuser
        instance = crinstance_assignment.CrAdminInstance(request=request)
        self.assertEqual([testassignment], list(instance.get_rolequeryset()))

    def test_get_rolequeryset_admin_on_period(self):
        testassignment = mommy.make('core.Assignment')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testassignment.period)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        instance = crinstance_assignment.CrAdminInstance(request=request)
        self.assertEqual([testassignment], list(instance.get_rolequeryset()))

    def test_get_rolequeryset_admin_on_subject(self):
        testassignment = mommy.make('core.Assignment')
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testassignment.subject)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        instance = crinstance_assignment.CrAdminInstance(request=request)
        self.assertEqual([testassignment], list(instance.get_rolequeryset()))
