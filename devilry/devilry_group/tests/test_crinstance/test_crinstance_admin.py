import mock
from django import test
from django.conf import settings
from model_bakery import baker

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_account import models as account_models
from devilry.devilry_group.cradmin_instances import crinstance_admin


class TestCrinstanceAdmin(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_rolequeryset_not_admin(self):
        baker.make('core.AssignmentGroup', parentnode=baker.make('core.Assignment'))
        testuser = baker.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        instance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertEqual([], list(instance.get_rolequeryset()))

    def test_get_rolequeryset_superuser(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode=baker.make('core.Assignment'))
        testuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        instance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertEqual([testgroup], list(instance.get_rolequeryset()))

    def test_get_rolequeryset_not_superuser(self):
        baker.make('core.AssignmentGroup', parentnode=baker.make('core.Assignment'))
        testuser = baker.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        instance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertEqual([], list(instance.get_rolequeryset()))

    def test_getrolequeryset_admin_on_period(self):
        testassignment = baker.make('core.Assignment')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                           period=testassignment.period)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup.permissiongroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        instance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertEqual([testgroup], list(instance.get_rolequeryset()))

    def test_getrolequeryset_not_admin_on_period(self):
        testassignment_another = baker.make('core.Assignment')
        testgroup_another = baker.make('core.AssignmentGroup', parentnode=testassignment_another)
        periodpermissiongroup_another = baker.make('devilry_account.PeriodPermissionGroup',
                                                   period=testassignment_another.period)
        testuser_another = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser_another,
                   permissiongroup=periodpermissiongroup_another.permissiongroup)

        testassignment = baker.make('core.Assignment')
        baker.make('core.AssignmentGroup', parentnode=testassignment)
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                           period=testassignment.period)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup.permissiongroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        instance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertNotEqual([testgroup_another], list(instance.get_rolequeryset()))

    def test_getrolequeryset_admin_on_subject(self):
        testassignment = baker.make('core.Assignment')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testassignment.subject)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup.permissiongroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        instance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertEqual([testgroup], list(instance.get_rolequeryset()))

    def test_getrolequeryset_not_admin_on_subject(self):
        testassignment_another = baker.make('core.Assignment')
        testgroup_another = baker.make('core.AssignmentGroup', parentnode=testassignment_another)
        subjectpermissiongroup_another = baker.make('devilry_account.SubjectPermissionGroup',
                                                    subject=testassignment_another.subject)
        testuser_another = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser_another,
                   permissiongroup=subjectpermissiongroup_another.permissiongroup)

        testassignment = baker.make('core.Assignment')
        baker.make('core.AssignmentGroup', parentnode=testassignment)
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testassignment.subject)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup.permissiongroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        instance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertNotEqual([testgroup_another], list(instance.get_rolequeryset()))

    def test_admin_devilryrole_periodadmin(self):
        testperiod = baker.make('core.Period')
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        testuser = baker.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor Thunder God')
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=baker.make(
                           'devilry_account.PeriodPermissionGroup',
                           permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN,
                           period=testperiod).permissiongroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        mockrequest.cradmin_role = testgroup
        testinstance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertEqual('periodadmin', testinstance.get_devilryrole_for_requestuser())

    def test_admin_devilryrole_subjectadmin(self):
        testsubject = baker.make('core.Subject')
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode__parentnode=testsubject)
        testuser = baker.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor Thunder God')
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=baker.make(
                           'devilry_account.SubjectPermissionGroup',
                           permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                           subject=testsubject).permissiongroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        mockrequest.cradmin_role = testgroup
        testinstance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertEqual('subjectadmin', testinstance.get_devilryrole_for_requestuser())
