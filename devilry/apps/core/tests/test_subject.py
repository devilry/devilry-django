from django import test
from django.conf import settings
from model_mommy import mommy

from devilry.apps.core.models import Subject


class TestSubjectQuerySetPermission(test.TestCase):
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


class TestSubjectQuerySetAnnotateWithHasActivePeriod(test.TestCase):
    def test_annotate_with_has_active_period_no_periods(self):
        mommy.make('core.Subject')
        annotated_subject = Subject.objects.annotate_with_has_active_period().first()
        self.assertFalse(annotated_subject.has_active_period)

    def test_annotate_with_has_active_period_only_old_periods(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_old', parentnode=testsubject)
        annotated_subject = Subject.objects.annotate_with_has_active_period().first()
        self.assertFalse(annotated_subject.has_active_period)

    def test_annotate_with_has_active_period_only_future_periods(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_future', parentnode=testsubject)
        annotated_subject = Subject.objects.annotate_with_has_active_period().first()
        self.assertFalse(annotated_subject.has_active_period)

    def test_annotate_with_has_active_period_has_active_period(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject)
        annotated_subject = Subject.objects.annotate_with_has_active_period().first()
        self.assertTrue(annotated_subject.has_active_period)

    def test_annotate_with_has_active_period_has_multiple_active_period(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject)
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject)
        annotated_subject = Subject.objects.annotate_with_has_active_period().first()
        self.assertTrue(annotated_subject.has_active_period)
