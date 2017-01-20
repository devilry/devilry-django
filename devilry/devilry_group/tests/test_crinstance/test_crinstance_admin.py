import mock
from django import test
from django.conf import settings
from model_mommy import mommy

from devilry.devilry_account import models as account_models
from devilry.devilry_group.cradmin_instances import crinstance_admin


class TestCrinstanceAdmin(test.TestCase):

    def test_get_rolequeryset_not_admin(self):
        mommy.make('core.AssignmentGroup', parentnode=mommy.make('core.Assignment'))
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        instance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertEquals([], list(instance.get_rolequeryset()))

    def test_get_rolequeryset_superuser(self):
        testgroup = mommy.make('core.AssignmentGroup', parentnode=mommy.make('core.Assignment'))
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        instance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertEqual([testgroup], list(instance.get_rolequeryset()))

    def test_get_rolequeryset_not_superuser(self):
        mommy.make('core.AssignmentGroup', parentnode=mommy.make('core.Assignment'))
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        instance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertEqual([], list(instance.get_rolequeryset()))

    def test_getrolequeryset_admin_on_period(self):
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testassignment.period)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup.permissiongroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        instance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertEquals([testgroup], list(instance.get_rolequeryset()))

    def test_getrolequeryset_not_admin_on_period(self):
        testassignment_another = mommy.make('core.Assignment')
        testgroup_another = mommy.make('core.AssignmentGroup', parentnode=testassignment_another)
        periodpermissiongroup_another = mommy.make('devilry_account.PeriodPermissionGroup',
                                                   period=testassignment_another.period)
        testuser_another = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser_another,
                   permissiongroup=periodpermissiongroup_another.permissiongroup)

        testassignment = mommy.make('core.Assignment')
        mommy.make('core.AssignmentGroup', parentnode=testassignment)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testassignment.period)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup.permissiongroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        instance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertNotEquals([testgroup_another], list(instance.get_rolequeryset()))

    def test_getrolequeryset_admin_on_subject(self):
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testassignment.subject)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup.permissiongroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        instance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertEquals([testgroup], list(instance.get_rolequeryset()))

    def test_getrolequeryset_not_admin_on_subject(self):
        testassignment_another = mommy.make('core.Assignment')
        testgroup_another = mommy.make('core.AssignmentGroup', parentnode=testassignment_another)
        subjectpermissiongroup_another = mommy.make('devilry_account.SubjectPermissionGroup',
                                                    subject=testassignment_another.subject)
        testuser_another = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser_another,
                   permissiongroup=subjectpermissiongroup_another.permissiongroup)

        testassignment = mommy.make('core.Assignment')
        mommy.make('core.AssignmentGroup', parentnode=testassignment)
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testassignment.subject)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup.permissiongroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        instance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertNotEquals([testgroup_another], list(instance.get_rolequeryset()))

    def test_admin_devilryrole_periodadmin(self):
        testperiod = mommy.make('core.Period')
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor Thunder God')
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=mommy.make(
                           'devilry_account.PeriodPermissionGroup',
                           permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN,
                           period=testperiod).permissiongroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        mockrequest.cradmin_role = testgroup
        testinstance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertEquals('periodadmin', testinstance.get_devilryrole_for_requestuser())

    def test_admin_devilryrole_subjectadmin(self):
        testsubject = mommy.make('core.Subject')
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode__parentnode=testsubject)
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor Thunder God')
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=mommy.make(
                           'devilry_account.SubjectPermissionGroup',
                           permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                           subject=testsubject).permissiongroup)
        mockrequest = mock.MagicMock()
        mockrequest.user = testuser
        mockrequest.cradmin_role = testgroup
        testinstance = crinstance_admin.AdminCrInstance(request=mockrequest)
        self.assertEquals('subjectadmin', testinstance.get_devilryrole_for_requestuser())
