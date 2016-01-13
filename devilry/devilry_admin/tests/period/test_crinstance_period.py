from django.conf import settings
from django.test import TestCase, RequestFactory
from model_mommy import mommy

from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_admin.views.period import crinstance_period


class TestCrAdminInstance(TestCase):
    def test_get_rolequeryset_not_admin(self):
        mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        request = RequestFactory().get('/test')
        request.user = testuser
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertEqual([], list(instance.get_rolequeryset()))

    def test_get_rolequeryset_superuser(self):
        testperiod = mommy.make('core.Period')
        request = RequestFactory().get('/test')
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        request.user = testuser
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertEqual([testperiod], list(instance.get_rolequeryset()))

    def test_get_rolequeryset_admin_on_period(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertEqual([testperiod], list(instance.get_rolequeryset()))

    def test_get_rolequeryset_admin_on_subject(self):
        testperiod = mommy.make('core.Period')
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testperiod.subject)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertEqual([testperiod], list(instance.get_rolequeryset()))

    def test_get_devilryrole_for_requestuser_not_admin(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testperiod
        instance = crinstance_period.CrAdminInstance(request=request)
        with self.assertRaises(ValueError):
            instance.get_devilryrole_for_requestuser()

    def test_get_devilryrole_for_requestuser_superuser(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testperiod
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertEqual('departmentadmin', instance.get_devilryrole_for_requestuser())

    def test_get_devilryrole_for_requestuser_subjectadmin(self):
        testperiod = mommy.make('core.Period')
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                            subject=testperiod.subject)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testperiod
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertEqual('subjectadmin', instance.get_devilryrole_for_requestuser())

    def test_get_devilryrole_for_requestuser_departmentadmin(self):
        testperiod = mommy.make('core.Period')
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN,
                                            subject=testperiod.subject)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testperiod
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertEqual('departmentadmin', instance.get_devilryrole_for_requestuser())

    def test_get_devilryrole_for_requestuser_periodadmin(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testperiod
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertEqual('periodadmin', instance.get_devilryrole_for_requestuser())

