from django.conf import settings
from django.test import TestCase
from model_mommy import mommy

from devilry.apps.core.models import Subject


class TestSubjectQuerySetPermission(TestCase):
    def test_filter_user_is_admin_is_not_admin_on_anything(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Subject')
        self.assertFalse(Subject.objects.filter_user_is_admin(user=testuser).exists())

    def test_filter_user_is_admin_superuser(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        testsubject = mommy.make('core.Subject')
        self.assertEqual(
            {testsubject},
            set(Subject.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_ignore_subjects_where_not_in_group(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testsubject = mommy.make('core.Subject')
        mommy.make('core.Subject')
        mommy.make('devilry_account.SubjectPermissionGroup',
                   subject=testsubject)
        self.assertFalse(Subject.objects.filter_user_is_admin(user=testuser).exists())

    def test_filter_user_is_admin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testsubject = mommy.make('core.Subject')
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        self.assertEqual(
            {testsubject},
            set(Subject.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_distinct(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testsubject = mommy.make('core.Subject')
        subjectpermissiongroup1 = mommy.make('devilry_account.SubjectPermissionGroup',
                                             subject=testsubject)
        subjectpermissiongroup2 = mommy.make('devilry_account.SubjectPermissionGroup',
                                             subject=testsubject)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup1.permissiongroup)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup2.permissiongroup)
        self.assertEqual(
            {testsubject},
            set(Subject.objects.filter_user_is_admin(user=testuser)))
