from __future__ import unicode_literals

from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import management
from django.core.management import CommandError
from model_mommy import mommy

from devilry.devilry_account.models import PermissionGroup, PermissionGroupUser, PeriodPermissionGroup


class TestPeriodadminclearCommand(test.TestCase):
    def __run_management_command(self, subject_short_name, period_short_name):
        management.call_command(
            'devilry_periodadminclear',
            subject_short_name, period_short_name)

    def test_invalid_subject_short_name(self):
        mommy.make('core.Period', short_name='testperiod')
        with self.assertRaisesMessage(CommandError,
                                      'Invalid subject_short_name.'):
            self.__run_management_command(subject_short_name='invalid',
                                          period_short_name='testperiod')

    def test_invalid_period_short_name(self):
        mommy.make('core.Subject', short_name='testsubject')
        with self.assertRaisesMessage(CommandError,
                                      'Invalid period_short_name.'):
            self.__run_management_command(subject_short_name='testsubject',
                                          period_short_name='invalid')

    def test_ok_no_permissiongroup(self):
        subject = mommy.make('core.Subject', short_name='testsubject')
        mommy.make('core.Period', short_name='testperiod', parentnode=subject)
        self.assertEqual(PermissionGroup.objects.count(), 0)
        self.__run_management_command(subject_short_name='testsubject',
                                      period_short_name='testperiod')
        self.assertEqual(PermissionGroup.objects.count(), 0)

    def test_ok_existing_permission_group(self):
        subject = mommy.make('core.Subject', short_name='testsubject')
        period = mommy.make('core.Period', short_name='testperiod', parentnode=subject)
        groupname = PermissionGroup.objects.get_name_from_syncsystem(
            basenode=period, grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN)
        permissiongroup = mommy.make(
            'devilry_account.PermissionGroup',
            name=groupname, is_custom_manageable=False,
            grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN)
        mommy.make('devilry_account.PeriodPermissionGroup',
                   permissiongroup=permissiongroup,
                   period=period)
        self.assertEqual(PermissionGroup.objects.count(), 1)
        self.assertEqual(PeriodPermissionGroup.objects.count(), 1)
        self.__run_management_command(subject_short_name='testsubject',
                                      period_short_name='testperiod')
        self.assertEqual(PermissionGroup.objects.count(), 0)
        self.assertEqual(PeriodPermissionGroup.objects.count(), 0)

    def test_ok_existing_permission_group_and_permission_group_user(self):
        user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser')
        subject = mommy.make('core.Subject', short_name='testsubject')
        period = mommy.make('core.Period', short_name='testperiod', parentnode=subject)
        groupname = PermissionGroup.objects.get_name_from_syncsystem(
            basenode=period, grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN)
        permissiongroup = mommy.make(
            'devilry_account.PermissionGroup',
            name=groupname, is_custom_manageable=False,
            grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN)
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=permissiongroup, user=user)
        self.assertEqual(PermissionGroupUser.objects.count(), 1)
        self.__run_management_command(subject_short_name='testsubject',
                                      period_short_name='testperiod')
        self.assertEqual(PermissionGroupUser.objects.count(), 0)
        self.assertTrue(get_user_model().objects.filter(id=user.id).exists())
