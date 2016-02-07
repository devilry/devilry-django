from django.conf import settings
from django.test import TestCase, RequestFactory
from model_mommy import mommy

from devilry.devilry_account.models import PermissionGroup
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

    def test_get_devilryrole_for_requestuser_not_admin(self):
        testassignment = mommy.make('core.Assignment')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testassignment
        instance = crinstance_assignment.CrAdminInstance(request=request)
        with self.assertRaises(ValueError):
            instance.get_devilryrole_for_requestuser()

    def test_get_devilryrole_for_requestuser_superuser(self):
        testassignment = mommy.make('core.Assignment')
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testassignment
        instance = crinstance_assignment.CrAdminInstance(request=request)
        self.assertEqual('departmentadmin', instance.get_devilryrole_for_requestuser())

    def test_get_devilryrole_for_requestuser_departmentadmin(self):
        testassignment = mommy.make('core.Assignment')
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN,
                                            subject=testassignment.subject)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testassignment
        instance = crinstance_assignment.CrAdminInstance(request=request)
        self.assertEqual('departmentadmin', instance.get_devilryrole_for_requestuser())

    def test_get_devilryrole_for_requestuser_subjectadmin(self):
        testassignment = mommy.make('core.Assignment')
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                            subject=testassignment.subject)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testassignment
        instance = crinstance_assignment.CrAdminInstance(request=request)
        self.assertEqual('subjectadmin', instance.get_devilryrole_for_requestuser())

    def test_get_devilryrole_for_requestuser_admin_periodadmin(self):
        testassignment = mommy.make('core.Assignment')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testassignment.period)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testassignment
        instance = crinstance_assignment.CrAdminInstance(request=request)
        self.assertEqual('periodadmin', instance.get_devilryrole_for_requestuser())

    def test_get_rolequeryset_uses_prefetch_point_to_grade_map(self):
        testassignment = mommy.make('core.Assignment')
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testassignment
        instance = crinstance_assignment.CrAdminInstance(request=request)
        assignment = instance.get_rolequeryset().first()
        self.assertTrue(hasattr(assignment, 'prefetched_point_to_grade_map'))
