from datetime import timedelta

from django import test
from django.conf import settings
from model_mommy import mommy

from devilry.apps.core.models import Subject
from devilry.apps.core.mommy_recipes import ACTIVE_PERIOD_START


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
    def test_no_periods(self):
        mommy.make('core.Subject')
        annotated_subject = Subject.objects.annotate_with_has_active_period().first()
        self.assertFalse(annotated_subject.has_active_period)

    def test_only_old_periods(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_old', parentnode=testsubject)
        annotated_subject = Subject.objects.annotate_with_has_active_period().first()
        self.assertFalse(annotated_subject.has_active_period)

    def test_only_future_periods(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_future', parentnode=testsubject)
        annotated_subject = Subject.objects.annotate_with_has_active_period().first()
        self.assertFalse(annotated_subject.has_active_period)

    def test_has_active_period(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject)
        annotated_subject = Subject.objects.annotate_with_has_active_period().first()
        self.assertTrue(annotated_subject.has_active_period)

    def test_has_multiple_active_period(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject)
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject)
        annotated_subject = Subject.objects.annotate_with_has_active_period().first()
        self.assertTrue(annotated_subject.has_active_period)


class TestSubjectQuerySetPrefetchActivePeriodobjects(test.TestCase):
    def test_no_periods(self):
        mommy.make('core.Subject')
        annotated_subject = Subject.objects.prefetch_active_periodobjects().first()
        self.assertEqual([], annotated_subject.active_period_objects)

    def test_only_old_periods(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_old', parentnode=testsubject)
        annotated_subject = Subject.objects.prefetch_active_periodobjects().first()
        self.assertEqual([], annotated_subject.active_period_objects)

    def test_only_future_periods(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_future', parentnode=testsubject)
        annotated_subject = Subject.objects.prefetch_active_periodobjects().first()
        self.assertEqual([], annotated_subject.active_period_objects)

    def test_has_active_period(self):
        testsubject = mommy.make('core.Subject')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject)
        annotated_subject = Subject.objects.prefetch_active_periodobjects().first()
        self.assertEqual([testperiod],
                         annotated_subject.active_period_objects)

    def test_has_multiple_active_periods_ordering(self):
        testsubject = mommy.make('core.Subject')
        testperiod1 = mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject)
        testperiod3 = mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject,
                                        start_time=ACTIVE_PERIOD_START + timedelta(days=60))
        testperiod2 = mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject,
                                        start_time=ACTIVE_PERIOD_START + timedelta(days=30))
        annotated_subject = Subject.objects.prefetch_active_periodobjects().first()
        self.assertEqual([testperiod1, testperiod2, testperiod3],
                         annotated_subject.active_period_objects)

    def test_querycount(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject)
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject,
                          start_time=ACTIVE_PERIOD_START + timedelta(days=30))
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject,
                          start_time=ACTIVE_PERIOD_START + timedelta(days=60))
        with self.assertNumQueries(2):
            annotated_subject = Subject.objects.prefetch_active_periodobjects().first()
            str(annotated_subject.active_period_objects[0].short_name)
            str(annotated_subject.active_period_objects[1].short_name)
            str(annotated_subject.active_period_objects[2].short_name)

    def test_last_active_period(self):
        testsubject = mommy.make('core.Subject')
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject)
        testperiod3 = mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject,
                                        start_time=ACTIVE_PERIOD_START + timedelta(days=60))
        mommy.make_recipe('devilry.apps.core.period_active', parentnode=testsubject,
                          start_time=ACTIVE_PERIOD_START + timedelta(days=30))
        annotated_subject = Subject.objects.prefetch_active_periodobjects().first()
        self.assertEqual(testperiod3, annotated_subject.last_active_period)
