import mock
from django.conf import settings
from django.http import Http404
from django.test import TestCase, RequestFactory
from model_mommy import mommy

from devilry.apps.core.models import Assignment
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

    def test_period_admin_access_restricted_period_has_no_semi_anonymous_assignments(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.Assignment', parentnode=testperiod)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testperiod
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertFalse(instance.period_admin_access_semi_anonymous_assignments_restricted())

    def test_period_admin_access_restricted_period_has_semi_anonymous_assignments(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.Assignment', parentnode=testperiod)
        mommy.make('core.Assignment', parentnode=testperiod,
                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testperiod
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertTrue(instance.period_admin_access_semi_anonymous_assignments_restricted())

    def test_period_admin_access_subject_admin_has_access(self):
        testsubject = mommy.make('core.Subject')
        testperiod = mommy.make('core.Period', parentnode=testsubject)
        mommy.make('core.Assignment', parentnode=testperiod)
        mommy.make('core.Assignment', parentnode=testperiod,
                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject,
                                            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testperiod
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertFalse(instance.period_admin_access_semi_anonymous_assignments_restricted())

    def test_period_admin_access_department_admin_has_access(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.Assignment', parentnode=testperiod)
        mommy.make('core.Assignment', parentnode=testperiod,
                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testperiod.subject,
                                            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testperiod
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertFalse(instance.period_admin_access_semi_anonymous_assignments_restricted())

    def test_period_admin_access_superuser_has_access(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.Assignment', parentnode=testperiod)
        mommy.make('core.Assignment', parentnode=testperiod,
                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testperiod
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertFalse(instance.period_admin_access_semi_anonymous_assignments_restricted())

    def test_get_role_from_rolequeryset_raises_404_for_qualifiesforexam_app_sanity(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.Assignment', parentnode=testperiod)
        mommy.make('core.Assignment', parentnode=testperiod,
                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testperiod

        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.appname = 'qualifiesforexam'
        request.cradmin_app = mock_cradmin_app
        instance = crinstance_period.CrAdminInstance(request=request)
        with self.assertRaises(Http404):
            instance.get_role_from_rolequeryset(role=testperiod)

    def test_get_role_from_rolequeryset_raises_404_for_overview_all_results_app_sanity(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.Assignment', parentnode=testperiod)
        mommy.make('core.Assignment', parentnode=testperiod,
                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testperiod

        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.appname = 'overview_all_results'
        request.cradmin_app = mock_cradmin_app
        instance = crinstance_period.CrAdminInstance(request=request)
        with self.assertRaises(Http404):
            instance.get_role_from_rolequeryset(role=testperiod)

    def test_get_role_from_rolequeryset_does_not_raise_404_for_other_apps(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.Assignment', parentnode=testperiod)
        mommy.make('core.Assignment', parentnode=testperiod,
                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testperiod

        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.appname = 'someapp'
        request.cradmin_app = mock_cradmin_app
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertEqual(testperiod, instance.get_role_from_rolequeryset(role=testperiod))

    def test_get_role_from_rolequeryset_does_not_raise_404_for_subject_admin(self):
        testsubject = mommy.make('core.Subject')
        testperiod = mommy.make('core.Period', parentnode=testsubject)
        mommy.make('core.Assignment', parentnode=testperiod)
        mommy.make('core.Assignment', parentnode=testperiod,
                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject,
                                            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        request.cradmin_role = testperiod

        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.appname = 'qualifiesforexam'
        request.cradmin_app = mock_cradmin_app
        instance = crinstance_period.CrAdminInstance(request=request)
        self.assertEqual(testperiod, instance.get_role_from_rolequeryset(role=testperiod))
