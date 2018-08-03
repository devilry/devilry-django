from django.conf import settings
from django.test import TestCase, RequestFactory
from model_mommy import mommy

from devilry.devilry_admin.views.subject_for_period_admin import crinstance_subject_for_periodadmin


class TestCrAdminInstance(TestCase):
    def test_get_rolequeryset_not_admin(self):
        mommy.make('core.Subject')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        request = RequestFactory().get('/test')
        request.user = testuser
        instance = crinstance_subject_for_periodadmin.CrAdminInstance(request=request)
        self.assertEqual([], list(instance.get_rolequeryset()))

    def test_get_rolequeryset_superuser(self):
        testsubject = mommy.make('core.Subject')
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        request = RequestFactory().get('/test')
        request.user = testuser
        instance = crinstance_subject_for_periodadmin.CrAdminInstance(request=request)
        self.assertEqual([testsubject], list(instance.get_rolequeryset()))

    def test_get_rolequeryset_periodadmin_within_subject(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        instance = crinstance_subject_for_periodadmin.CrAdminInstance(request=request)
        self.assertEqual([testperiod.parentnode], list(instance.get_rolequeryset()))

    def test_get_rolequeryset_admin_on_subject(self):
        testsubject = mommy.make('core.Subject')
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=subjectpermissiongroup.permissiongroup)
        request = RequestFactory().get('/test')
        request.user = testuser
        instance = crinstance_subject_for_periodadmin.CrAdminInstance(request=request)
        self.assertEqual([testsubject], list(instance.get_rolequeryset()))
